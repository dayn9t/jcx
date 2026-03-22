"""Error handling utilities.

This module provides helper functions for working with optional values
and displaying errors in a consistent format.
"""

import traceback
from collections.abc import Callable
from typing import Any, TypeVar

from loguru import logger
from rustshed import Err

T = TypeVar("T")


def mand(value: T | None) -> T:
    """Force an optional value to be non-null.

    Asserts that the value is not None and returns it.
    Use this when you are certain a value exists but the type system
    cannot guarantee it.

    Args:
        value: Optional value that must not be None.

    Returns:
        The value if not None.

    Raises:
        AssertionError: If value is None.

    """
    assert value is not None
    return value


def show_err(e: Any) -> None:
    """Display an error or exception in a formatted way.

    Handles different error types and logs them with appropriate formatting.

    Args:
        e: Error or exception to display. Can be:
            - Err: rustshed Result error variant
            - AssertionError: Python assertion failure
            - Other: Any other error type

    """
    if isinstance(e, Err):
        msg = f"{e}"
    # elif isinstance(e, UnwrapError):
    #    msg = 'UnwrapError(%s):' % str(e.result.value)
    elif isinstance(e, AssertionError):
        msg = f"AssertionError({e.args})"
    else:
        msg = f"UnknownError({e!r})"
    logger.error(msg)


def catch_show_err(fun: Callable[[], Any], verbose: bool = False) -> None:
    """Execute a function and catch/display any exceptions.

    Catches all exceptions except SystemExit, KeyboardInterrupt, and
    GeneratorExit. Logs the error and optionally prints the traceback.

    Args:
        fun: Function to execute.
        verbose: If True, print full traceback on error.

    """
    # 捕获SystemExit/KeyboardInterrupt/GeneratorExit外异常
    # 想捕获这三个异常, 需BaseException
    try:
        fun()
    except Exception as e:
        show_err(e)
        # print('traceback.print_exc():', traceback.print_exc())
        if verbose:
            print(traceback.format_exc())


def show_err_demo() -> None:
    """Demo function showing error display behavior."""
    e = Err("a error")
    print(type(e))
    show_err(e)


if __name__ == "__main__":
    show_err_demo()
