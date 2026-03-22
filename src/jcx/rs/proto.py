"""Protocol for cloneable types.

This module defines a protocol for types that support cloning via deep copy.
"""

from copy import deepcopy
from typing import Protocol, Self, TypeVar

C = TypeVar("C", bound="Cloned")


class Cloned(Protocol):
    """Protocol for types that support deep cloning.

    Any type that implements this protocol provides a clone() method
    that returns a deep copy of itself.

    Example:
        >>> from jcx.rs.proto import Cloned
        >>> @dataclass
        ... class Point:
        ...     x: int
        ...     y: int
        ...     def clone(self) -> Self:
        ...         return deepcopy(self)

    """

    def clone(self) -> Self:
        """Create a deep copy of this instance.

        Returns:
            A new instance that is a deep copy of self.

        Example:
            >>> point = Point(1, 2)
            >>> copy = point.clone()
            >>> copy is point
            False

        """
        return deepcopy(self)
