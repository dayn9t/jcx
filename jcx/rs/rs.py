from typing import TypeVar

from rustshed import Null, Option, Some

from jcx.rs.proto import Cloned

T = TypeVar("T")

C = TypeVar("C", bound=Cloned)


def rs_option(v: T | None) -> Option[T]:
    """Optional => Option"""
    if v is None:
        return Null
    return Some(v)


def rs_option_cloned(v: C | None) -> Option[C]:
    """Optional => Option & cloned"""
    if v is None:
        return Null
    return Some(v.clone())


def py_optional(v: Option[T]) -> T | None:
    """Option => Optional"""
    if v.is_null():
        return None
    return v.unwrap()
