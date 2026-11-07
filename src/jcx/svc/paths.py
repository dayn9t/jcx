"""Tree-root resolution and tree-internal relative path resolution.

Services deployed inside a versioned tree (``<root>/<app>/bin/<exe>``) must not
hard-code the version segment in their configs: a config file's location already
encodes the tree, so tree-internal file references are written *relative to the
config file's directory* and resolved at load time. This module holds the two
mechanisms:

1. root resolution — from an anchor inside the tree (usually the running
   executable) back up to the tree root, by fixed depth or by marker search;
2. relative reference resolution — rewrite ``*{suffix}`` fields of a loaded
   pydantic config in place against the config file's directory, rejecting
   absolute values (they reintroduce exactly the version-segment coupling the
   relative form exists to eliminate).

Promoted & generalized from downstream ``avs_common/paths.py`` (2026-11-07):
semantics preserved, all downstream naming/path assumptions stripped — root
location strategy is parameterized instead of assumed.
"""

from __future__ import annotations

import sys
from pathlib import Path

from pydantic import BaseModel
from rustshed import Err, Null, Ok, Option, Result, Some

from jcx.sys.fs import StrPath


def program_file() -> Option[Path]:
    """Entry file of the running program (``__main__.__file__``).

    The usual anchor for root resolution. ``Null`` when the program has no
    entry file (REPL, some frozen executables) — the caller must then supply
    an anchor explicitly instead of guessing.
    """
    file = getattr(sys.modules.get("__main__"), "__file__", None)
    return Some(Path(file)) if isinstance(file, str) else Null


def root_by_depth(anchor: StrPath, levels: int = 1) -> Result[Path, ValueError]:
    """Tree root as exactly ``levels`` parent hops above ``anchor``.

    ``levels=1`` is the anchor's own directory. For a service executable at
    ``<root>/<app>/bin/<exe>`` the root is three hops up (bin → app → root);
    a source-tree layout resolves with a different ``levels`` — the strategy
    is the caller's parameter, never an assumption here.

    Fail-loud: ``levels < 1`` or fewer than ``levels`` ancestors above the
    anchor → ``Err`` (a wrong root would silently misplace every tree-relative
    lookup downstream — No Silent Degradation).
    """
    if levels < 1:
        return Err(ValueError(f"levels must be >= 1, got {levels}"))
    path = Path(anchor).resolve()
    if len(path.parents) < levels:
        return Err(ValueError(f"only {len(path.parents)} ancestors above {anchor}, need {levels}"))
    return Ok(path.parents[levels - 1])


def root_by_marker(anchor: StrPath, marker: StrPath) -> Option[Path]:
    """First directory at or above ``anchor`` containing ``marker``.

    Self-validating alternative to :func:`root_by_depth`: the tree root is
    identified by a marker file/directory (e.g. ``cfg/``) instead of counted
    levels. ``anchor`` itself counts when it is a directory; otherwise the
    search starts at its parent. ``Null`` when no ancestor up to the
    filesystem root carries the marker.
    """
    d = Path(anchor)
    if not d.is_dir():
        d = d.parent
    for candidate in (d, *d.parents):
        if (candidate / marker).exists():
            return Some(candidate)
    return Null


def resolve_rel_paths[M: BaseModel](
    cfg: M, cfg_file: StrPath, *, suffix: str = "_path"
) -> Result[None, ValueError]:
    """Resolve tree-internal relative references in ``cfg`` in place.

    Contract (fail-loud):

    - fields named ``*{suffix}`` with a non-``None`` value must be relative;
      they are joined onto ``cfg_file``'s directory and written back in place;
    - an absolute value → ``Err`` naming the field: absolute paths hard-code
      the version segment (or reach outside the tree) and are never allowed
      to pass silently;
    - nested pydantic submodels are traversed recursively; elements inside
      containers (list/dict) are not — extend when a config shape needs it;
    - atomic: on ``Err`` nothing is mutated.
    """
    base = Path(cfg_file).resolve().parent
    plan: list[tuple[BaseModel, str, Path]] = []
    violations: list[str] = []
    _collect(cfg, base, prefix=type(cfg).__name__, suffix=suffix, plan=plan, violations=violations)
    if violations:
        return Err(ValueError("; ".join(violations)))
    for model, name, resolved in plan:
        setattr(model, name, resolved)
    return Ok(None)


def _collect(
    model: BaseModel,
    base: Path,
    *,
    prefix: str,
    suffix: str,
    plan: list[tuple[BaseModel, str, Path]],
    violations: list[str],
) -> None:
    """Single traversal: recurse submodels, plan relative rewrites, record violations."""
    for name in type(model).model_fields:
        value = getattr(model, name)
        if isinstance(value, BaseModel):
            _collect(
                value,
                base,
                prefix=f"{prefix}.{type(value).__name__}",
                suffix=suffix,
                plan=plan,
                violations=violations,
            )
            continue
        if not name.endswith(suffix) or value is None:
            continue
        rel = Path(str(value))
        if rel.is_absolute():
            violations.append(
                f"{prefix}.{name}: absolute path {rel!s} not allowed — "
                "tree-internal references must be relative to the cfg file's directory"
            )
            continue
        plan.append((model, name, base / rel))
