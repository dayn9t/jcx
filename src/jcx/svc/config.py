"""Layered config loading for versioned deployment trees.

Config ships in layers — a per-node override layer on top of a shipped default
layer (or any ordered stack the caller configures). Loading semantics (canon:
ias ``load_cfg``, ``docs/2026-11-07-data-plane-and-migration-design.md`` §1):

- layers are searched in the given order; the first layer holding the config
  wins (earlier layers override later ones);
- a *missing* candidate (open-stage file-not-found) is the only legal
  fall-through signal — it moves the search to the next candidate;
- a candidate that exists but cannot be read, parsed, or validated → ``Err``
  naming the file. Silently skipping a corrupt override layer would serve the
  stale default under the operator's feet (No Silent Degradation);
- all candidates missing → ``Err`` listing every searched path — a fabricated
  default model is never substituted;
- dual format: each layer's config may be json5 or yaml; within one layer the
  suffixes are tried in :data:`CFG_SUFFIXES` order, so a layer holding both
  resolves deterministically (json5 first).

Promoted & generalized (2026-11-07) from ias ``load_cfg`` (json5 two-level,
Rust) and the downstream yaml loader: format support merged, layer list opened
to any length, zero downstream path assumptions.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import json5
import yaml
from pydantic import BaseModel
from rustshed import Err, Ok, Result

from jcx.sys.fs import StrPath

CFG_SUFFIXES: tuple[str, ...] = (".json5", ".yaml", ".yml")
"""Suffix search order for one config name within a layer."""


def load_cfg_file[C: BaseModel](file: StrPath, model_type: type[C]) -> Result[C, Exception]:
    """Load and validate one config file (json5 or yaml, by suffix).

    Error contract consumed by :func:`load_layered_cfg`:

    - ``Err(FileNotFoundError)`` — file missing (the legal fall-through signal);
    - ``Err(OSError)`` — file exists but cannot be read (permissions, …);
    - ``Err(ValueError)`` — file exists but is corrupt or fails validation;
      the message names the file.

    The parsed root must be a mapping; anything else is a deployment error and
    is rejected rather than coerced into the model.
    """
    f = Path(file)
    try:
        text = f.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        return Err(e)
    except OSError as e:
        return Err(OSError(f"cfg exists but unreadable: {f}: {e}"))
    try:
        data = json5.loads(text) if f.suffix == ".json5" else yaml.safe_load(text)
        if not isinstance(data, dict):
            return Err(ValueError(f"cfg {f}: root must be a mapping, got {type(data).__name__}"))
        cfg = model_type.model_validate(data)
    except (ValueError, yaml.YAMLError) as e:
        # json5 parse and pydantic validation raise ValueError subclasses;
        # yaml raises YAMLError — both mean "exists but corrupt", fail loud.
        return Err(ValueError(f"failed to load cfg {f}: {e}"))
    return Ok(cfg)


def load_layered_cfg[C: BaseModel](
    model_type: type[C],
    name: str,
    layers: Sequence[StrPath],
) -> Result[C, Exception]:
    """Load config ``name`` from the first layer that holds it.

    Args:
        model_type: pydantic model the file content is validated into.
        name: config stem (without suffix); each layer is searched for
            ``name`` + each suffix in :data:`CFG_SUFFIXES` order.
        layers: directories in precedence order — the first layer holding the
            config wins (override-first, e.g. ``[node_dir, default_dir]``).

    Returns:
        ``Ok`` with the validated model from the first layer that holds it.
        ``Err(FileNotFoundError)`` when no candidate exists anywhere (message
        lists all searched paths); any other ``Err`` names the corrupt file
        and aborts the search — never falls through past an existing file.
    """
    if not layers:
        return Err(ValueError("no config layers configured"))
    candidates = [Path(layer) / f"{name}{ext}" for layer in layers for ext in CFG_SUFFIXES]
    for f in candidates:
        result = load_cfg_file(f, model_type)
        if result.is_ok():
            return result
        # Missing is the only legal fall-through; anything else fails loud.
        if not isinstance(result.unwrap_err(), FileNotFoundError):
            return result
    searched = ", ".join(str(c) for c in candidates)
    return Err(FileNotFoundError(f"cfg '{name}' not found in any layer; searched: {searched}"))
