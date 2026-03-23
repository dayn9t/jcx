---
phase: 1-pydantic-v2-frozenmodel
plan: 1
subsystem: jcx.m
tags: [pydantic, enum, immutability, type-safety]
dependencies:
  requires: [pydantic>=2.0]
  provides: [FrozenModel, EnumItem, PydanticEnum]
  affects: []
tech_stack:
  added: [pydantic.ConfigDict, pydantic.BaseModel, enum.Enum]
  patterns: [frozen-model, enum-with-metadata]
key_files:
  created:
    - src/jcx/m/enum.py
    - tests/m/enum_test.py
  modified:
    - src/jcx/m/__init__.py
decisions:
  - Use ConfigDict for model_config following existing pattern in calendar_type.py
  - FrozenModel combines frozen=True with extra="forbid" for strict validation
  - PydanticEnum properties return typed values from EnumItem
metrics:
  duration: 2 min
  completed_date: 2026-03-23
  tasks_completed: 1
  files_modified: 3
---

# Phase 1-pydantic-v2-frozenmodel Plan 1: Pydantic V2 FrozenModel Summary

## One-liner

Added immutable Pydantic V2 base classes (FrozenModel, EnumItem, PydanticEnum) for creating enum-like data structures with rich metadata.

## What Was Done

Created `src/jcx/m/enum.py` with three interconnected classes:

1. **FrozenModel** - Abstract base class inheriting from BaseModel with `frozen=True` and `extra="forbid"` configuration for strict immutability.

2. **EnumItem** - Data class inheriting from FrozenModel with three fields:
   - `value: int` - Integer value of the enum member
   - `name: str` - String name identifier
   - `description: str = ""` - Optional human-readable description (defaults to empty string)

3. **PydanticEnum** - Generic enum base class that uses EnumItem as member values, providing convenient properties:
   - `value_int` - Returns the integer value
   - `name_str` - Returns the string name
   - `description` - Returns the description

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Use ConfigDict for model_config | Follows existing pattern in `calendar_type.py` |
| Combine frozen=True with extra="forbid" | Ensures strict immutability and validation |
| PydanticEnum inherits from Enum | Leverages Python's standard enum behavior for iteration and member access |

## Files Changed

| File | Action | Purpose |
|------|--------|---------|
| `src/jcx/m/enum.py` | Created | Main implementation |
| `src/jcx/m/__init__.py` | Modified | Export new classes |
| `tests/m/enum_test.py` | Created | Test coverage |

## Deviations from Plan

None - plan executed exactly as written.

## Self-Check: PASSED

- [x] `from jcx.m.enum import FrozenModel, EnumItem, PydanticEnum` succeeds
- [x] FrozenModel instances are immutable (tested with ValidationError on assignment)
- [x] EnumItem has value, name, description fields (tested with defaults)
- [x] PydanticEnum subclasses work with EnumItem values (tested with ColorEnum example)
- [x] All 8 tests pass
- [x] Commit 79bc934 exists
