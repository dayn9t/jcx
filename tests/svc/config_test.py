"""Tests for jcx.svc.config: layered loading semantics (override/fall-through/fail-loud)."""

from pathlib import Path

from pydantic import BaseModel

from jcx.svc.config import load_cfg_file, load_layered_cfg


class Cfg(BaseModel):
    host: str
    port: int


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_first_layer_wins(tmp_path: Path) -> None:
    node = tmp_path / "node"
    default = tmp_path / "default"
    write(node / "svc.json5", "{host: '127.0.0.1', port: 9001}")
    write(default / "svc.json5", "{host: '0.0.0.0', port: 8001}")
    result = load_layered_cfg(Cfg, "svc", [node, default])
    assert result.unwrap().port == 9001


def test_missing_layer_falls_through(tmp_path: Path) -> None:
    node = tmp_path / "node"  # empty layer
    node.mkdir()
    default = tmp_path / "default"
    write(default / "svc.yaml", "host: 127.0.0.1\nport: 8001\n")
    result = load_layered_cfg(Cfg, "svc", [node, default])
    assert result.unwrap().port == 8001


def test_yaml_and_json5_both_load(tmp_path: Path) -> None:
    layer = tmp_path / "a"
    write(layer / "one.yaml", "host: h1\nport: 1\n")
    write(layer / "two.json5", "{host: 'h2', port: 2}")
    assert load_layered_cfg(Cfg, "one", [layer]).unwrap().port == 1
    assert load_layered_cfg(Cfg, "two", [layer]).unwrap().port == 2


def test_suffix_precedence_within_layer(tmp_path: Path) -> None:
    layer = tmp_path / "a"
    write(layer / "svc.json5", "{host: 'h', port: 1}")
    write(layer / "svc.yaml", "host: h\nport: 2\n")
    # deterministic: json5 is tried before yaml
    assert load_layered_cfg(Cfg, "svc", [layer]).unwrap().port == 1


def test_corrupt_json5_fails_loud_no_fallback(tmp_path: Path) -> None:
    node = tmp_path / "node"
    default = tmp_path / "default"
    write(node / "svc.json5", "{host: 'h', port: ")  # unparseable
    write(default / "svc.json5", "{host: 'ok', port: 8001}")
    result = load_layered_cfg(Cfg, "svc", [node, default])
    assert result.is_err()
    msg = str(result.unwrap_err())
    # names the corrupt file; must NOT have served the default layer
    assert "svc.json5" in msg
    assert "node" in msg


def test_corrupt_yaml_fails_loud(tmp_path: Path) -> None:
    node = tmp_path / "node"
    write(node / "svc.yaml", "host: [unclosed\n")
    result = load_layered_cfg(Cfg, "svc", [node])
    assert result.is_err()
    assert "svc.yaml" in str(result.unwrap_err())


def test_invalid_content_fails_loud(tmp_path: Path) -> None:
    layer = tmp_path / "a"
    write(layer / "svc.yaml", "host: h\nport: not-an-int\n")
    result = load_layered_cfg(Cfg, "svc", [layer])
    assert result.is_err()
    assert "svc.yaml" in str(result.unwrap_err())


def test_non_mapping_root_fails_loud(tmp_path: Path) -> None:
    layer = tmp_path / "a"
    write(layer / "svc.yaml", "- just\n- a list\n")
    result = load_layered_cfg(Cfg, "svc", [layer])
    assert result.is_err()
    assert "mapping" in str(result.unwrap_err())


def test_unreadable_candidate_fails_loud(tmp_path: Path) -> None:
    layer = tmp_path / "a"
    layer.mkdir()
    # a directory where the config file should be: exists, but cannot be read
    (layer / "svc.json5").mkdir()
    result = load_layered_cfg(Cfg, "svc", [layer])
    assert result.is_err()
    assert not isinstance(result.unwrap_err(), FileNotFoundError)


def test_all_layers_missing_lists_candidates(tmp_path: Path) -> None:
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir()
    b.mkdir()
    result = load_layered_cfg(Cfg, "svc", [a, b])
    assert result.is_err()
    err = result.unwrap_err()
    assert isinstance(err, FileNotFoundError)
    # honest report: every searched candidate is named
    msg = str(err)
    for c in (a / "svc.json5", a / "svc.yaml", b / "svc.json5"):
        assert str(c) in msg


def test_no_layers_is_error() -> None:
    assert load_layered_cfg(Cfg, "svc", []).is_err()


def test_load_cfg_file_json5(tmp_path: Path) -> None:
    f = tmp_path / "svc.json5"
    write(f, "// comment\n{host: 'h', port: 1}")
    assert load_cfg_file(f, Cfg).unwrap().port == 1


def test_load_cfg_file_yaml(tmp_path: Path) -> None:
    f = tmp_path / "svc.yml"
    write(f, "host: h\nport: 1\n")
    assert load_cfg_file(f, Cfg).unwrap().port == 1


def test_load_cfg_file_missing(tmp_path: Path) -> None:
    result = load_cfg_file(tmp_path / "nope.json5", Cfg)
    assert result.is_err()
    assert isinstance(result.unwrap_err(), FileNotFoundError)
