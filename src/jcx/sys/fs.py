"""File system utilities for path manipulation and file operations.

This module provides helper functions for working with files and directories,
including finding files, creating directories, and timestamp-based file naming.
"""

import re
import shutil
import sys
from collections.abc import Callable, Generator
from enum import Enum
from pathlib import Path
from typing import Any

import arrow
import sh
from arrow import Arrow
from loguru import logger
from parse import parse
from rustshed import Err, Null, Ok, Option, Result, Some

type Paths = list[Path]
"""路径数组"""

type StrPath = str | Path
"""路径表示: str或者Path"""

type StrPaths = list[StrPath]
"""可表示路径类型的数组"""


class Order(Enum):
    """排序方式."""

    ASC = 1
    DESC = 2


def first_file_in(folders: StrPaths, file_name: str) -> Option[Path]:
    """Search for a specific file in a list of directories, returning the first match.

    Args:
        folders: List of directory paths to search.
        file_name: Name of the file to find.

    Returns:
        Some(Path) if the file is found in any directory, Null otherwise.

    """
    for p in folders:
        f = Path(p) / file_name
        if f.is_file():
            return Some(f)
    return Null


def files_in(folder: StrPath, ext: str, reverse: bool = False) -> list[Path]:
    """Get sorted list of files with specified extension in a folder.

    Args:
        folder: Directory path to search.
        ext: File extension to filter (e.g., ".txt").
        reverse: If True, sort in descending order.

    Returns:
        Sorted list of Path objects matching the extension.

    """
    p = Path(folder)
    return sorted(p.glob("*" + ext), reverse=reverse)


def get_project_dir(bin_file: StrPath) -> Path:
    """Get the project root directory from an executable file path.

    Assumes the executable is located at /project/src/bin/exe_file.py.

    Args:
        bin_file: Path to the executable file.

    Returns:
        Resolved path to the project root directory.

    """
    # /project/src/bin/exe_file.py
    return Path(bin_file).parent.parent.parent.resolve()


def get_asset_dir(bin_file: StrPath) -> Path:
    """Get the project asset directory from an executable file path.

    Args:
        bin_file: Path to the executable file.

    Returns:
        Path to the project's asset directory.

    """
    return get_project_dir(bin_file) / "asset"


def file_names_in(folder: StrPath, ext: str, reverse: bool = False) -> list[str]:
    """Get sorted list of file names with specified extension in a folder.

    Args:
        folder: Directory path to search.
        ext: File extension to filter.
        reverse: If True, sort in descending order.

    Returns:
        Sorted list of file names (including extension).

    """
    return [f.name for f in files_in(folder, ext, reverse)]


def file_stems_in(folder: StrPath, ext: str, reverse: bool = False) -> list[str]:
    """Get sorted list of file stems (names without extension) in a folder.

    Args:
        folder: Directory path to search.
        ext: File extension to filter.
        reverse: If True, sort in descending order.

    Returns:
        Sorted list of file stems (names without extension).

    """
    return [f.stem for f in files_in(folder, ext, reverse)]


def find(src: StrPath, ext: str, order: Order = Order.ASC) -> list[Path]:
    """Find files with specified extension in a file or directory.

    Args:
        src: File path or directory to search.
        ext: File extension to filter.
        order: Sort order (ASC or DESC).

    Returns:
        Sorted list of matching file paths. Empty list if source doesn't exist.

    """
    src = Path(src)
    if src.is_dir():
        files = sorted(src.rglob("*" + ext), reverse=(order == Order.DESC))
    elif src.is_file():
        files = [src]
    else:
        files = []
    return files


def find_first(
    folder: StrPath,
    pattern: str,
    recursive: bool = True,
) -> Result[Path, str]:
    """Find the first file matching a glob pattern in a directory.

    Args:
        folder: Directory path to search.
        pattern: Glob pattern to match (e.g., "*.txt", "**/config.json").
        recursive: If True, search recursively; otherwise, search only top level.

    Returns:
        Ok(Path) if a matching file is found, Err with error message otherwise.

    """
    folder = Path(folder)
    if not folder.is_dir():
        return Err("指定路径不是目录: " + str(folder))

    it = folder.rglob(pattern) if recursive else folder.glob(pattern)
    try:
        f = next(it)
    except StopIteration:
        return Err("指定文件找不到: " + pattern)
    return Ok(f)


def find_in_parts(folder: StrPath, sub_path: str) -> Option[Path]:
    """Search for a path in parent directories by walking up the directory tree.

    Args:
        folder: Starting directory path.
        sub_path: Relative path to search for.

    Returns:
        Some(Path) if found in any parent directory, Null if not found.

    """
    folder = Path(folder).absolute()
    while True:
        path = folder / sub_path
        if path.exists():
            return Some(path)
        folder = folder.parent
        if folder == folder.parent:
            break
    return Null


def file_exist_in(folder: StrPath, pattern: str, recursive: bool = False) -> bool:
    """Check if any file matching the pattern exists in the directory.

    Args:
        folder: Directory path to search.
        pattern: Glob pattern to match.
        recursive: If True, search recursively.

    Returns:
        True if at least one matching file exists, False otherwise.

    """
    return find_first(folder, pattern, recursive).is_ok()


def dirs_in(folder: StrPath, order: Order = Order.ASC) -> list[Path]:
    """Get list of subdirectories in a folder.

    Args:
        folder: Directory path to search.
        order: Sort order (ASC or DESC).

    Returns:
        Sorted list of subdirectory paths. Empty list if folder doesn't exist.

    """
    folder = Path(folder)
    dirs: Paths = []
    if not folder.is_dir():
        return dirs
    for f in folder.iterdir():
        if f.is_dir():
            dirs.append(f)
    if order:
        return sorted(dirs, reverse=(order == Order.DESC))
    return dirs


def find_descendants(folder: StrPath, pattern: str, generation: int) -> list[Path]:
    """Find files/directories matching a pattern at a specific generation depth.

    Args:
        folder: Root directory to start search.
        pattern: Glob pattern to match.
        generation: Depth level (1 = immediate children, 2 = grandchildren, etc.).

    Returns:
        Sorted list of matching paths at the specified generation.

    Raises:
        AssertionError: If generation is less than 1.

    """
    assert generation > 0
    folder = Path(folder)

    if generation == 1:
        return sorted(folder.glob(pattern))

    children = dirs_in(folder)
    descendants = []
    for child in children:
        d = find_descendants(child, pattern, generation - 1)
        descendants.extend(d)
    return descendants


def rm_files_in(folder: StrPath, ext: str) -> None:
    """Delete all files with specified extension in a folder.

    Args:
        folder: Directory path to clean.
        ext: File extension to delete (e.g., ".tmp").

    """
    for f in Path(folder).glob("*" + ext):
        Path(f).unlink()


def remake_dir(path: StrPath) -> Path:
    """Delete and recreate a directory.

    If the directory exists, it is removed and recreated.
    If it doesn't exist, it is created along with any parent directories.

    Args:
        path: Directory path to recreate.

    Returns:
        The recreated Path object.

    """
    p = Path(path)
    if p.exists():
        shutil.rmtree(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def remake_subdir(parent: StrPath, name: str) -> Path:
    """Delete and recreate a subdirectory.

    Args:
        parent: Parent directory path.
        name: Name of the subdirectory.

    Returns:
        The recreated subdirectory Path object.

    """
    return make_subdir(parent, name, True)


def make_subdir(parent: StrPath, name: str, remake: bool = False) -> Path:
    """Create a subdirectory, optionally recreating if it exists.

    Args:
        parent: Parent directory path.
        name: Name of the subdirectory.
        remake: If True, delete existing subdirectory before creating.

    Returns:
        The created subdirectory Path object.

    """
    path = Path(parent, name)
    if path.exists() and remake:
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def make_parents(p: StrPath) -> Path:
    """Create parent directories for a file path.

    Args:
        p: File path whose parent directories should be created.

    Returns:
        The parent directory Path object.

    """
    p = Path(p).parent
    p.mkdir(parents=True, exist_ok=True)
    return p


def or_ext(file: StrPath, ext: str) -> Path:
    """Add extension to file path if it doesn't have one.

    Args:
        file: File path.
        ext: Extension to add (including the dot, e.g., ".txt").

    Returns:
        Path with extension added if it was missing.

    """
    file = Path(file)
    if not file.suffix and ext:
        file = file.with_suffix(ext)
    return file


def last_parts(file: StrPath, n: int) -> Path:
    """Get the last n parts of a file path.

    Args:
        file: File path.
        n: Number of path parts to keep from the end.

    Returns:
        Path containing only the last n parts.

    """
    p = Path(file)
    return Path(*p.parts[-n:])


def with_parent(file: StrPath, parent: str) -> Path:
    """Replace the parent directory name in a file path.

    Args:
        file: Original file path.
        parent: New parent directory name.

    Returns:
        Path with the parent directory name replaced.

    """
    file = Path(file)
    return file.parent.parent / parent / file.name


def find_pattern(folder: StrPath, ext: str, pattern: str) -> Generator[Path, Any, None]:
    """Find files matching a regex pattern within files of specified extension.

    Args:
        folder: Directory to search recursively.
        ext: File extension to filter.
        pattern: Regex pattern to match against file paths.

    Yields:
        Path objects for files whose paths match the pattern.

    """
    for f in Path(folder).rglob("*" + ext):
        if re.search(pattern, str(f)):
            yield f


def time_to_file(time: Arrow, ext: str, date_dir: bool = True) -> str:
    """Convert an Arrow time to a filename string.

    Args:
        time: Arrow datetime object.
        ext: File extension to append.
        date_dir: If True, use "/" separator (for date subdirs).
                  If False, use "_" separator (for flat filenames).

    Returns:
        Filename string in format "YYYY-MM-DD_HH-MM-SS.mmm<ext>" or
        "YYYY-MM-DD/HH-MM-SS.mmm<ext>".

    """
    s = "/" if date_dir else "_"
    fmt = "%Y-%m-%d" + s + "%H-%M-%S.%f"
    name = time.strftime(fmt)[:-3] + ext
    return name


def device_time_file(
    folder: Path,
    dev_id: int | str,
    time: Arrow,
    ext: str,
    date_dir: bool = True,
) -> Path:
    """Create a timestamp-based file path for a device.

    Args:
        folder: Base directory for the device.
        dev_id: Device identifier (used as subdirectory name).
        time: Arrow datetime for the filename.
        ext: File extension.
        date_dir: If True, create date subdirectories.

    Returns:
        Full path to the timestamped file, with parent directories created.

    """
    file = time_to_file(time, ext, date_dir)
    p = Path(folder, str(dev_id), file)
    make_parents(p)
    return p


def not_file_to_time(path: StrPath) -> Arrow:
    """Parse time from a timestamped filename (inverse of time_to_file).

    Expects filename format: 2023-04-10_10-09-39.830
    The parent directory name is used as the date part.

    Args:
        path: File path with timestamped name.

    Returns:
        Arrow datetime parsed from the path.

    """
    p = Path(path)
    s = "{}T{}+{}".format(p.parent.name, p.stem.replace("-", ":"), "08:00")
    return arrow.get(s)


def link_files(
    src_files: list[Path],
    dst_dir: Path,
    check_fun: Callable[[Path], bool] | None = None,
) -> None:
    """Create symbolic links for a list of files in a destination directory.

    Args:
        src_files: List of source file paths to link.
        dst_dir: Destination directory for the links.
        check_fun: Optional validation function called on each created link.
                   If it returns False, an error is logged.

    """
    for f in src_files:
        dst = dst_dir / f.name
        dst.parent.mkdir(exist_ok=True, parents=True)
        dst.symlink_to(f.absolute())
        if check_fun and not check_fun(dst):
            logger.error(f"check fail: {dst}")


def real_path(path: StrPath) -> Path:
    """Get the real path of a file, resolving symbolic links.

    Args:
        path: File path, potentially a symlink.

    Returns:
        The target path if it's a symlink, otherwise the original path.

    """
    p = Path(path)
    return Path.readlink(p) if p.is_symlink() else p


def real_exe_path() -> Path:
    """Get the real path of the currently running executable.

    Resolves symbolic links to find the actual executable file.

    Returns:
        Real path of sys.argv[0].

    """
    return real_path(sys.argv[0])


def copy_file(src: Path, dst: Path) -> Result[Path, IOError]:
    """Copy a file to a destination, creating parent directories if needed.

    Args:
        src: Source file path.
        dst: Destination file path.

    Returns:
        Ok(dst) on success, Err with IOError on failure.

    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copyfile(src, dst)
    except OSError as e:
        return Err(e)
    return Ok(dst)


def move_file(src: Path, dst: Path) -> Result[Path, IOError]:
    """Move a file to a destination, creating parent directories if needed.

    Args:
        src: Source file path.
        dst: Destination file path.

    Returns:
        Ok(dst) on success, Err with IOError on failure.

    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.move(src, dst)
    except OSError as e:
        return Err(e)
    return Ok(dst)


def insert_dir(folder: StrPath, dir_name: str) -> None:
    """Insert a new directory level inside an existing directory.

    Moves all contents of the folder into a new subdirectory with the given name.

    Args:
        folder: Directory to modify.
        dir_name: Name of the new subdirectory to create inside.

    Raises:
        AssertionError: If folder is not a directory.

    """
    folder = Path(folder)
    assert folder.is_dir()
    tmp = folder.parent / (folder.name + "_tmp")
    dst = folder / dir_name
    shutil.move(folder, tmp)

    assert not folder.exists()
    folder.mkdir()
    assert folder.exists()
    shutil.move(tmp, dst)


def file_ctime(file: StrPath) -> Arrow:
    """Get the creation time of a file.

    Args:
        file: Path to the file.

    Returns:
        Arrow datetime of the file's creation time.

    """
    t = Path(file).stat().st_ctime  # 创建时间
    return Arrow.fromtimestamp(t)


def file_mtime(file: StrPath) -> Arrow:
    """Get the modification time of a file.

    Args:
        file: Path to the file.

    Returns:
        Arrow datetime of the file's modification time.

    """
    t = Path(file).stat().st_mtime  # 创建时间
    return Arrow.fromtimestamp(t)


def ctime_to_name(src: Path) -> str:
    """Generate a filename based on the file's creation time.

    Args:
        src: Path to the source file.

    Returns:
        Timestamped filename string with the original extension.

    """
    return time_to_file(file_ctime(src), src.suffix)


def mtime_to_name(src: Path) -> str:
    """Generate a filename based on the file's modification time.

    Args:
        src: Path to the source file.

    Returns:
        Timestamped filename string with the original extension.

    """
    return time_to_file(file_mtime(src), src.suffix)


class FileTimeIterator:
    """Iterator that generates sequential timestamp-based file paths.

    Each call to __next__ returns a Path with a timestamp that is
    1 second later than the previous one. Useful for generating
    unique file names for sequential files.

    Example:
        start_time = Arrow.now()
        iterator = FileTimeIterator(Path("/photos"), start_time, ".jpg")
        path1 = next(iterator)  # /photos/2026-03-21_14-30-00.000.jpg
        path2 = next(iterator)  # /photos/2026-03-21_14-30-01.000.jpg

    """

    def __init__(self, base_path: Path, start_time: Arrow, ext: str = ".jpg"):
        """Initialize the iterator.

        Args:
            base_path: Directory path for generated file paths
            start_time: Starting timestamp (Arrow object)
            ext: File extension including the dot (default: ".jpg")

        """
        self._base_path = base_path
        self._current = start_time
        self._ext = ext

    def __iter__(self) -> "FileTimeIterator":
        """Return self as iterator."""
        return self

    def __next__(self) -> Path:
        """Generate next file path with sequential timestamp.

        Returns:
            Path object with timestamp-based filename

        """
        result = self._base_path / time_to_file(
            self._current, self._ext, date_dir=False
        )
        self._current = self._current.shift(seconds=1)
        return result

    def peek(self) -> Path:
        """Get current path without advancing the iterator.

        Returns:
            Path object for current timestamp

        """
        return self._base_path / time_to_file(self._current, self._ext, date_dir=False)

    def reset(self, start_time: Arrow) -> None:
        """Reset iterator to a new start time.

        Args:
            start_time: New starting timestamp

        """
        self._current = start_time


def stem_append(p: Path, s: str) -> Path:
    """文件名主干后面追加字符串."""
    return p.parent / (p.stem + s + p.suffix)


def name_with_parents(path: StrPath, num_parents: int) -> Option[str]:
    """路径转换成文件名, 文件名中带有指定数量的上级目录, REMARK: 避免上级目录中包含根目录."""
    parts = list(Path(path).parts)
    start = len(parts) - 1 - num_parents
    if start < 0:
        return Null
    name = "_".join(parts[start:])
    return Some(name)


def replace_home(p: StrPath) -> Path:
    """替换~为HOME目录."""
    p = str(p).replace("~", str(Path.home()))
    return Path(p)


def remove_parent_prefix(p: StrPath) -> Result[Path, str]:
    """从文件名中去掉所在目录名前缀."""
    p = Path(p)
    if p.name.startswith(p.parent.name):
        p1 = p.parent / p.name[len(p.parent.name) + 1 :]
        return Ok(p1)
    return Err("No prefix")


def du(path: StrPath) -> int:
    """获取文件或目录的大小."""
    s = sh.du("-s", path)
    size, _ = parse("{}\t{}", s)
    return int(size)
