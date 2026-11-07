"""Tests for jcx.svc.paths: root resolution + tree-internal relative resolution."""

from pathlib import Path

from pydantic import BaseModel

from jcx.svc.paths import (
    program_file,
    resolve_rel_paths,
    root_by_depth,
    root_by_marker,
)


def test_root_by_depth(tmp_path: Path) -> None:
    exe = tmp_path / "app" / "bin" / "svc"
    exe.parent.mkdir(parents=True)
    exe.touch()
    # <root>/app/bin/exe → root is three parent hops up
    result = root_by_depth(exe, 3)
    assert result.unwrap() == tmp_path.resolve()


def test_root_by_depth_one_level(tmp_path: Path) -> None:
    f = tmp_path / "file.txt"
    f.touch()
    assert root_by_depth(f).unwrap() == tmp_path.resolve()


def test_root_by_depth_rejects_bad_levels() -> None:
    assert root_by_depth("/a/b/c", 0).is_err()
    # /a/b/c has 3 ancestors (/a/b, /a, /); asking for more is an error
    result = root_by_depth("/a/b/c", 5)
    assert result.is_err()


def test_root_by_marker(tmp_path: Path) -> None:
    (tmp_path / "cfg").mkdir()
    deep = tmp_path / "app" / "bin" / "svc"
    deep.parent.mkdir(parents=True)
    deep.touch()
    found = root_by_marker(deep, "cfg")
    assert found.unwrap() == tmp_path.resolve()


def test_root_by_marker_accepts_marker_file(tmp_path: Path) -> None:
    (tmp_path / ".tree-root").touch()
    f = tmp_path / "a" / "b.txt"
    f.parent.mkdir()
    f.touch()
    assert root_by_marker(f, ".tree-root").unwrap() == tmp_path.resolve()


def test_root_by_marker_missing(tmp_path: Path) -> None:
    f = tmp_path / "a" / "b.txt"
    f.parent.mkdir()
    f.touch()
    # no ancestor up to / carries the marker
    assert not root_by_marker(f, "no-such-marker-xyz").is_some()


def test_program_file() -> None:
    # under pytest, __main__ is the pytest entry script and has a __file__
    result = program_file()
    assert result.is_some()
    assert result.unwrap().is_absolute()


class Inner(BaseModel):
    hotwords_path: str | None = None


class Cfg(BaseModel):
    name: str
    data_path: str
    sub: Inner
    items: list[Inner] = []


def test_resolve_rel_paths(tmp_path: Path) -> None:
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir()
    cfg_file = cfg_dir / "svc.json5"
    cfg_file.touch()

    cfg = Cfg(name="a", data_path="hotwords.txt", sub=Inner(hotwords_path="dic/main.txt"))
    assert resolve_rel_paths(cfg, cfg_file).is_ok()
    # resolved values are absolute Paths anchored at the cfg file's directory
    assert Path(cfg.data_path) == (cfg_dir / "hotwords.txt").resolve()
    assert Path(cfg.sub.hotwords_path) == (cfg_dir / "dic" / "main.txt").resolve()
    # non-suffix and None fields untouched
    assert cfg.name == "a"


def test_resolve_rel_paths_none_value_untouched(tmp_path: Path) -> None:
    cfg_file = tmp_path / "svc.yaml"
    cfg_file.touch()
    cfg = Cfg(name="a", data_path="x.bin", sub=Inner())
    assert resolve_rel_paths(cfg, cfg_file).is_ok()
    assert cfg.sub.hotwords_path is None


def test_resolve_rel_paths_rejects_absolute(tmp_path: Path) -> None:
    cfg_file = tmp_path / "cfg" / "svc.json5"
    cfg_file.parent.mkdir()
    cfg_file.touch()
    cfg = Cfg(
        name="a",
        data_path="/opt/sln/v0.10/cfg/hotwords.txt",
        sub=Inner(),
    )
    result = resolve_rel_paths(cfg, cfg_file)
    assert result.is_err()
    msg = str(result.unwrap_err())
    assert "Cfg.data_path" in msg
    assert "absolute" in msg


def test_resolve_rel_paths_atomic_on_error(tmp_path: Path) -> None:
    cfg_file = tmp_path / "svc.json5"
    cfg_file.touch()
    cfg = Cfg(name="a", data_path="ok.txt", sub=Inner(hotwords_path="/abs/dic.txt"))
    assert resolve_rel_paths(cfg, cfg_file).is_err()
    # the relative sibling was NOT mutated although it sorts first
    assert cfg.data_path == "ok.txt"


def test_resolve_rel_paths_custom_suffix(tmp_path: Path) -> None:
    cfg_file = tmp_path / "svc.json5"
    cfg_file.touch()

    class DirCfg(BaseModel):
        data_dir: str

    cfg = DirCfg(data_dir="tables")
    assert resolve_rel_paths(cfg, cfg_file, suffix="_dir").is_ok()
    assert Path(cfg.data_dir) == (tmp_path / "tables").resolve()


def test_resolve_rel_paths_containers_not_traversed(tmp_path: Path) -> None:
    """Documented boundary: elements inside list/dict containers stay unresolved."""
    cfg_file = tmp_path / "svc.json5"
    cfg_file.touch()
    cfg = Cfg(
        name="a",
        data_path="x.bin",
        sub=Inner(),
        items=[Inner(hotwords_path="nested.txt")],
    )
    assert resolve_rel_paths(cfg, cfg_file).is_ok()
    assert cfg.items[0].hotwords_path == "nested.txt"
