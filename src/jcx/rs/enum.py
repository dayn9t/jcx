"""Pydantic V2 immutable enum base classes.

This module provides reusable patterns for immutable enum-like data structures
using Pydantic V2's frozen models and Python's enum module.

Example:
    >>> from jcx.rs.enum import EnumItem, RichEnum
    >>>
    >>> class Status(RichEnum):
    ...     ACTIVE = EnumItem(value=1, name="active", description="Active status")
    ...     INACTIVE = EnumItem(value=2, name="inactive", description="Inactive status")
    >>>
    >>> Status.ACTIVE.value_int
    1
    >>> Status.ACTIVE.name_str
    'active'
    >>> Status.ACTIVE.description
    'Active status'

"""

from enum import Enum

from pydantic import BaseModel, ConfigDict


class FrozenModel(BaseModel):
    """Immutable Pydantic V2 base class.

    Use this as a base class for Pydantic models that should be immutable
    after creation. Combines frozen=True with extra="forbid" for strict
    validation.

    Example:
        >>> from jcx.rs.enum import FrozenModel
        >>>
        >>> class Point(FrozenModel):
        ...     x: int
        ...     y: int
        >>> p = Point(x=1, y=2)
        >>> p.x = 5  # Raises ValidationError
    """

    model_config = ConfigDict(frozen=True, extra="forbid")


class EnumItem(FrozenModel):
    """Immutable enum item with value, name, and description.

    This is the data class used as member values in RichEnum.
    Each enum member stores its integer value, string name, and optional
    description.

    Attributes:
        value: Integer value of the enum member.
        name: String name identifier for the enum member.
        description: Human-readable description (defaults to empty string).

    Example:
        >>> item = EnumItem(value=1, name="first", description="First item")
        >>> item.value
        1
        >>> item.name
        'first'
        >>> item.description
        'First item'
    """

    value: int
    name: str
    description: str = ""


class RichEnum(Enum):
    """Enum base class with rich metadata (value, name, description).

    Inherit from this class to create enums with rich metadata.
    Each member should be assigned an EnumItem containing value,
    name, and optional description.

    Properties provide convenient access to the EnumItem fields:
        - value_int: The integer value
        - name_str: The string name
        - description: The human-readable description

    Example:
        >>> class Priority(RichEnum):
        ...     LOW = EnumItem(value=1, name="low", description="Low priority")
        ...     HIGH = EnumItem(value=2, name="high", description="High priority")
        >>> Priority.LOW.value_int
        1
        >>> Priority.HIGH.name_str
        'high'
        >>> list(Priority)  # Iteration works normally
        [<Priority.LOW: EnumItem(value=1, name='low', description='Low priority')>, ...]
    """

    @property
    def value_int(self) -> int:
        """Get integer value of this enum member."""
        item: EnumItem = self.value
        return item.value

    @property
    def name_str(self) -> str:
        """Get string name of this enum member."""
        item: EnumItem = self.value
        return item.name

    @property
    def description(self) -> str:
        """Get description of this enum member."""
        item: EnumItem = self.value
        return item.description
