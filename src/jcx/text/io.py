"""Basic text file I/O utilities.

This module provides simple functions for reading and writing text files
with proper error handling using the Result type.
"""

from rustshed import Err, Ok, Result

from jcx.sys.fs import StrPath, or_ext


def load_txt(file: StrPath) -> Result[str, str]:
    """Load text content from a file.

    Args:
        file: Path to the file to load.

    Returns:
        Ok(str) with file content on success, Err with error message on failure.

    """
    with open(file) as f:
        s = f.read()
        return Ok(s)
    # return Err('load_txt fail.')


def save_txt(txt: str, file: StrPath, ext: str = ".txt") -> Result[bool, Exception]:
    """Save text content to a file.

    Creates parent directories if they don't exist.

    Args:
        txt: Text content to save.
        file: Path to the output file (extension added if missing).
        ext: Extension to add if file has no extension.

    Returns:
        Ok(True) on success, Err with exception on failure.

    """
    file = or_ext(file, ext)
    try:
        file.parent.mkdir(parents=True, exist_ok=True)
        with open(file, "w") as f:
            f.write(txt)
    except PermissionError:
        return Err(PermissionError(f"权限不足: {file}"))
    except OSError as e:
        return Err(OSError(f"写入文件失败 {file}: {e}"))
    return Ok(True)


def save_lines(
    lines: list[str],
    file: StrPath,
    ext: str = "",
    postfix: str = "",
) -> None:
    r"""Save a list of strings as lines to a file.

    Creates parent directories if they don't exist. Each line is written
    with the specified postfix appended (typically a newline).

    Args:
        lines: List of strings to write as lines.
        file: Path to the output file (extension added if specified).
        ext: Extension to add if file has no extension.
        postfix: String to append after each line (e.g., "\n").

    """
    file = or_ext(file, ext)
    file.parent.mkdir(parents=True, exist_ok=True)
    print("save:", file)
    with open(file, "w") as f:
        f.writelines(line + postfix for line in lines)


def replace_in_file(
    src_file: StrPath,
    input_: str,
    output: str,
    dst_file: StrPath | None = None,
) -> Result[bool, str]:
    """Replace text in a file.

    Reads the source file, replaces all occurrences of input_ with output,
    and writes to the destination file.

    Args:
        src_file: Path to the source file to read.
        input_: Text to search for.
        output: Text to replace with.
        dst_file: Path to the output file (defaults to src_file for in-place edit).

    Returns:
        Ok(True) on success, Err with error message on failure.

    """
    dst_file = dst_file or src_file

    result = load_txt(src_file)
    if result.is_err():
        return Err(f"Failed to load {src_file}: {result.unwrap_err()}")
    txt = result.unwrap()
    new_data = txt.replace(input_, output)
    save_result = save_txt(new_data, dst_file)
    if save_result.is_err():
        return Err(f"Failed to save {dst_file}: {save_result.unwrap_err()}")
    return Ok(True)
