"""Re-exports of rustshed Result/Option types for convenient importing.

This module provides a stable import path for Result and Option types,
re-exporting from the rustshed library.

Example:
    from jcx.rs import Result, Ok, Err, Option, Some, Null

    def divide(a: int, b: int) -> Result[float, str]:
        if b == 0:
            return Err("Division by zero")
        return Ok(a / b)
"""

from rustshed import (
    Err,
    IOResult,
    Null,
    NullType,
    Ok,
    Option,
    Result,
    Some,
    is_err,
    is_null,
    is_ok,
    is_some,
    to_io_result,
    to_option,
    to_result,
)

__all__ = [
    "Err",
    "IOResult",
    "Null",
    "NullType",
    "Ok",
    "Option",
    "Result",
    "Some",
    "is_err",
    "is_null",
    "is_ok",
    "is_some",
    "to_io_result",
    "to_option",
    "to_result",
]
