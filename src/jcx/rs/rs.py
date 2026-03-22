"""Conversion utilities between Python Optional and rustshed Option types.

This module provides helper functions to convert between Python's Optional[T]
(which is T | None) and rustshed's Option[T] type for better interoperability.
"""

from typing import TypeVar

from rustshed import Null, Option, Some

from jcx.rs.proto import Cloned

T = TypeVar("T")

C = TypeVar("C", bound=Cloned)


def rs_option(v: T | None) -> Option[T]:
    """Convert a Python Optional value to rustshed Option.

    Args:
        v: A Python Optional value (T | None).

    Returns:
        Option[T] containing Some(v) if v is not None, otherwise Null.

    Example:
        >>> rs_option(42)
        Some(42)
        >>> rs_option(None)
        Null

    """
    if v is None:
        return Null
    return Some(v)


def rs_option_cloned(v: C | None) -> Option[C]:
    """Convert a Python Optional value to rustshed Option with cloning.

    This function is useful when you need an owned copy of the value
    rather than a reference. The value must implement the Cloned protocol.

    Args:
        v: A Python Optional value implementing the Cloned protocol.

    Returns:
        Option[C] containing Some(v.clone()) if v is not None, otherwise Null.

    Example:
        >>> from dataclasses import dataclass
        >>> @dataclass
        ... class Point:
        ...     x: int
        ...     y: int
        ...     def clone(self):
        ...         return Point(self.x, self.y)
        >>> rs_option_cloned(Point(1, 2))
        Some(Point(x=1, y=2))

    """
    if v is None:
        return Null
    return Some(v.clone())


def py_optional(v: Option[T]) -> T | None:
    """Convert a rustshed Option to Python Optional.

    Args:
        v: A rustshed Option[T] value.

    Returns:
        T | None containing the value if Some, otherwise None.

    Raises:
        UnwrapError: If the Option is Null (should not happen with is_null check).

    Example:
        >>> from rustshed import Some
        >>> py_optional(Some(42))
        42
        >>> py_optional(Null)
        None

    """
    if v.is_null():
        return None
    return v.expect("Option was Null in py_optional conversion")
