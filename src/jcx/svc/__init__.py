"""Microservice scaffolding: tree-root resolution, layered config, FastAPI shell.

Promoted & generalized from downstream service commons (2026-11-07 promotion
discipline: renamed, stripped of every downstream naming/path assumption).
Mechanisms live here; deployment-tree conventions live in the ias design canon
(``docs/2026-11-07-data-plane-and-migration-design.md`` §1/§4).

Requires the ``svc`` extra (``fastapi`` + ``pyyaml``) for :mod:`jcx.svc.config`
and :mod:`jcx.svc.app`; :mod:`jcx.svc.paths` is dependency-light (pydantic only).
"""
