from rustshed import Err, Ok, Result

from jcx.sys.fs import StrPath, or_ext


def load_txt(file: StrPath) -> Result[str, str]:
    """加载文本"""
    with open(file) as f:
        s = f.read()
        return Ok(s)
    # return Err('load_txt fail.')


def save_txt(txt: str, file: StrPath, ext: str = ".txt") -> Result[bool, Exception]:
    """保存文本到文件"""
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
    """多行文本保存到文件, 文件自动加扩展名, 自动建立目录, 行尾自动加回车"""
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
    """文本文件替换

    Returns:
        Result[bool, str]: Ok(True) on success, Err with error message on failure

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
