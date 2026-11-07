"""Generic FastAPI microservice shell: assembly + healthz/readyz + cfg injection.

The reusable template a deployed service wraps around its typed config:

- the validated pydantic config instance is injected as ``app.state.cfg``
  (handlers read it via ``request.app.state.cfg``);
- ``GET /healthz`` — liveness, always 200;
- ``GET /readyz`` — readiness: 200 when the ``ready`` predicate holds (or when
  none is given), 503 otherwise;
- optional ``lifespan`` passthrough for startup/shutdown resource ownership.

Capability endpoints are added by the caller on the returned app — this shell
stays at the scaffolding layer and binds no capability, backend, or model-dir
convention. Promoted & generalized from downstream ``avs_common/app.py``
(2026-11-07): the single-GPU endpoint gate, backend factory contract, and
model-dir environment variable of the downstream original are application
concerns and were deliberately left out.
"""

from collections.abc import Callable
from contextlib import AbstractAsyncContextManager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# NOTE: ``from __future__ import annotations`` is deliberately omitted (same
# reason as the downstream original): FastAPI reads handler annotations at
# decoration time to bind response schemas; concrete runtime types are required.
type LifespanFactory = Callable[[FastAPI], AbstractAsyncContextManager[None]]
"""Async context manager factory handed to FastAPI's ``lifespan`` parameter."""


def build_app[C: BaseModel](
    cfg: C,
    *,
    title: str,
    version: str = "0.1.0",
    ready: Callable[[], bool] | None = None,
    lifespan: LifespanFactory | None = None,
) -> FastAPI:
    """Assemble a microservice app around a typed config instance.

    Args:
        cfg: validated config model; injected as ``app.state.cfg``.
        title: service title (OpenAPI).
        version: service version (OpenAPI).
        ready: readiness predicate; ``None`` means always ready.
        lifespan: startup/shutdown resource ownership (FastAPI semantics).

    Returns:
        The assembled app; callers add their capability endpoints on it.
    """
    app = FastAPI(title=title, version=version, lifespan=lifespan)
    app.state.cfg = cfg

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz")
    def readyz() -> JSONResponse:
        if ready is not None and not ready():
            return JSONResponse(status_code=503, content={"status": "not ready"})
        return JSONResponse(status_code=200, content={"status": "ready"})

    return app
