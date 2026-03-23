---
phase: 1-pydantic-v2-frozenmodel
plan: 1
type: execute
wave: 1
depends_on: []
files_modified: [src/jcx/m/enum.py, src/jcx/m/__init__.py]
autonomous: true
requirements: []
user_setup: []

must_haves:
  truths:
    - "FrozenModel is immutable and cannot be modified after creation"
    - "EnumItem has value, name, description fields"
    - "EnumItem forbids extra fields"
    - "PydanticEnum provides value_int, name_str, description properties"
  artifacts:
    - path: "src/jcx/m/enum.py"
      provides: "FrozenModel, EnumItem, PydanticEnum"
      exports: ["FrozenModel", "EnumItem", "PydanticEnum"]
  key_links:
    - from: "EnumItem"
      to: "FrozenModel"
      via: "inheritance"
      pattern: "class EnumItem\\(FrozenModel\\)"
    - from: "PydanticEnum"
      to: "EnumItem"
      via: "member type"
      pattern: "_value_: EnumItem"
---

<objective>
Define Pydantic V2 immutable enum base classes: FrozenModel, EnumItem, and PydanticEnum.

Purpose: Provide a reusable pattern for immutable enum-like data structures with Pydantic V2.
Output: New module `src/jcx/m/enum.py` with FrozenModel, EnumItem, and PydanticEnum classes.
</objective>

<execution_context>
@/home/jiang/.claude/get-shit-done/workflows/execute-plan.md
@/home/jiang/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
## Locked Decisions (from CONTEXT.md - MUST honor)

1. **Implementation:** Inherit from `FrozenModel` for immutability
2. **Config:** Use `model_config = {"extra": "forbid"}` to reject extra fields
3. **Fields:** Three fields: `value: int`, `name: str`, `description: str = ""`
4. **Serialization:** Use Pydantic defaults (model_dump, model_validate), no custom logic

## Existing Pattern

From `src/jcx/time/calendar_type.py`:
```python
from pydantic import BaseModel, ConfigDict

class ClockPeriod(BaseModel):
    model_config: ConfigDict = ConfigDict(frozen=True)
    begin: ClockTime = ClockTime()
    end: ClockTime = ClockTime()
```

## Target Location

`src/jcx/m/enum.py` - matches existing utility modules in `jcx/m/` directory.
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Create FrozenModel, EnumItem, and PydanticEnum</name>
  <files>src/jcx/m/enum.py, src/jcx/m/__init__.py</files>
  <behavior>
    - Test 1: FrozenModel instance is immutable (raises error on attribute assignment)
    - Test 2: EnumItem has value, name, description fields
    - Test 3: EnumItem rejects extra fields with validation error
    - Test 4: PydanticEnum member returns correct value_int, name_str, description
    - Test 5: PydanticEnum iteration yields all members
  </behavior>
  <action>
    Create `src/jcx/m/enum.py` with:

    1. **FrozenModel** - Abstract base class:
       ```python
       from pydantic import BaseModel, ConfigDict

       class FrozenModel(BaseModel):
           """Immutable Pydantic V2 base class."""
           model_config = ConfigDict(frozen=True, extra="forbid")
       ```

    2. **EnumItem** - Enum member data class:
       ```python
       class EnumItem(FrozenModel):
           """Immutable enum item with value, name, description."""
           value: int
           name: str
           description: str = ""
       ```

    3. **PydanticEnum** - Generic enum base class:
       ```python
       from enum import Enum
       from typing import TypeVar

       T = TypeVar("T", bound=EnumItem)

       class PydanticEnum(Enum):
           """Enum base class using EnumItem as member values."""

           @property
           def value_int(self) -> int:
               """Get integer value of this enum member."""
               return self.value.value

           @property
           def name_str(self) -> str:
               """Get string name of this enum member."""
               return self.value.name

           @property
           def description(self) -> str:
               """Get description of this enum member."""
               return self.value.description
       ```

    4. Update `src/jcx/m/__init__.py` to export the new classes.

    Follow existing code style from `calendar_type.py`: use ConfigDict for model_config.
  </action>
  <verify>
    <automated>python -c "from jcx.m.enum import FrozenModel, EnumItem, PydanticEnum; print('OK')"</automated>
  </verify>
  <done>
    - FrozenModel is immutable BaseModel with extra="forbid"
    - EnumItem inherits FrozenModel with value/name/description fields
    - PydanticEnum provides value_int, name_str, description properties
    - Module imports successfully
  </done>
</task>

</tasks>

<verification>
Run Python import test to verify module structure is correct.
</verification>

<success_criteria>
- `from jcx.m.enum import FrozenModel, EnumItem, PydanticEnum` succeeds
- FrozenModel instances are immutable
- EnumItem has value, name, description fields
- PydanticEnum subclasses work with EnumItem values
</success_criteria>

<output>
After completion, create `.planning/quick/1-pydantic-v2-frozenmodel/1-SUMMARY.md`
</output>
