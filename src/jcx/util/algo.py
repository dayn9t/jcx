"""Algorithm utilities for lookup and comparison operations.

This module provides helper functions for searching dictionaries, finding
elements in lists, and determining insertion positions.
"""

from typing import Any, TypeVar

from rustshed import Null, Option, Some, to_option

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")


def lookup(indexes: list[int], tab: list[T]) -> list[T]:
    """Look up values by indexes in a table.

    Args:
        indexes: List of index positions (0-based).
        tab: Table to look up values from.

    Returns:
        List of values at the corresponding indexes in tab.

    """
    return [tab[i] for i in indexes]


def dict_first_key(d: dict[K, V], value: V) -> Option[K]:
    """Find the first key that maps to the given value in a dictionary.

    Args:
        d: Dictionary to search.
        value: Value to search for.

    Returns:
        Some(K) if found, Null otherwise.

    """
    for k, v in d.items():
        if v == value:
            return Some(k)

    return Null


def low_pos(arr: list[T], value: T) -> int:
    """Find the smallest insertion position for a value in a sorted list.

    Args:
        arr: Sorted list to search in.
        value: Value to find insertion position for.

    Returns:
        The index where value should be inserted to maintain sorted order.
        Returns len(arr) if value is greater than all elements.

    """
    for i, v in enumerate(arr):
        # Generic T cannot be constrained to Comparable; runtime comparison is acceptable
        if value <= v:  # type: ignore[operator]
            return i
    return len(arr)


def up_pos(arr: list[T], value: T) -> int:
    """Find the largest insertion position for a value in a sorted list.

    Args:
        arr: Sorted list to search in.
        value: Value to find insertion position for.

    Returns:
        The index where value should be inserted (upper bound).
        Returns len(arr) if value is greater than or equal to all elements.

    """
    for i, v in enumerate(arr):
        # Generic T cannot be constrained to Comparable; runtime comparison is acceptable
        if value < v:  # type: ignore[operator]
            return i
    return len(arr)


@to_option
def list_index(arr: list[T], value: T) -> int:
    """Find the index of a value in a list, returning Null if not found.

    Args:
        arr: List to search.
        value: Value to find.

    Returns:
        Some(int) if found, Null if not found.

    """
    # list.index returns Any for generic T; to_option wrapper handles TypeError if value not found
    return arr.index(value)  # type: ignore[no-any-return]
