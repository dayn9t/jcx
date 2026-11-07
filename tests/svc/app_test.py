"""Tests for jcx.svc.app: FastAPI shell (healthz/readyz + cfg injection)."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel

from jcx.svc.app import build_app


class Cfg(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8001


def test_healthz_always_200() -> None:
    client = TestClient(build_app(Cfg(), title="svc-test"))
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_readyz_without_predicate_is_ready() -> None:
    client = TestClient(build_app(Cfg(), title="svc-test"))
    r = client.get("/readyz")
    assert r.status_code == 200
    assert r.json() == {"status": "ready"}


def test_readyz_predicate_false_gives_503() -> None:
    client = TestClient(build_app(Cfg(), title="svc-test", ready=lambda: False))
    assert client.get("/readyz").status_code == 503


def test_readyz_predicate_true_gives_200() -> None:
    client = TestClient(build_app(Cfg(), title="svc-test", ready=lambda: True))
    assert client.get("/readyz").status_code == 200


def test_cfg_injected_on_state() -> None:
    cfg = Cfg(port=9009)
    app = build_app(cfg, title="svc-test")
    assert app.state.cfg is cfg


def test_caller_adds_endpoints_on_the_shell() -> None:
    """The shell is a template: downstream capability endpoints compose with it."""
    app = build_app(Cfg(), title="svc-test")

    @app.get("/port")
    def port(request: Request) -> dict[str, int]:
        cfg: Cfg = request.app.state.cfg
        return {"port": cfg.port}

    client = TestClient(app)
    assert client.get("/port").json() == {"port": 8001}


def test_title_and_version_propagate() -> None:
    app = build_app(Cfg(), title="svc-x", version="1.2.3")
    assert app.title == "svc-x"
    assert app.version == "1.2.3"


def test_lifespan_passthrough() -> None:
    events: list[str] = []

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        events.append("startup")
        yield
        events.append("shutdown")

    app = build_app(Cfg(), title="svc-test", lifespan=lifespan)
    with TestClient(app) as client:
        assert client.get("/healthz").status_code == 200
        assert events == ["startup"]
    assert events == ["startup", "shutdown"]
