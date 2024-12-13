import tempfile

from jcx.sys.fs import *


def find_pattern_del() -> None:
    """删除垃圾消息文件"""
    folder = "/var/ias/snapshot/shtm/n1/work/"
    # folder = '/var/ias/snapshot/shtm/n1/work/100500101'
    # folder = '/var/ias/snapshot/shtm/n1/work/902400111'
    i = 0
    for f in find_pattern(folder, ".msg", "2021-08"):
        # print(str(f))
        f.unlink()
        i += 1
    print("删除文件:", i)


def find_first_test() -> None:
    folder = "/opt/ias/meta/work"
    f = find_first(folder, "*.json")
    print(f)
    f = find_first(folder, "?9.json")
    print(f)
    f = find_first(folder, "31.json")
    print(f)
    b = file_exist_in(folder, "*.json")
    print(b)
    b = file_exist_in(folder, "*.json", True)
    print(b)


def test_find_parts() -> None:
    p = find_in_parts("/usr/local/lib/1", "bin")
    assert str(p.unwrap()) == "/usr/local/bin"


def fs_test() -> None:
    folder = Path("/tmp/fs_test")
    folder.mkdir(exist_ok=True)
    assert folder.exists()

    for i in range(10):
        Path(folder, "%d.json" % i).touch()

    for f in folder.glob("*.json"):
        print(f)

    files = files_in(folder, ".json")
    print(files)
    print(type(files))

    for f in files:
        print(f)
        # print(type(f))

    rm_files_in(folder, ".json")
    files = files_in(folder, ".json")
    print(files)


def test_dirs_in() -> None:
    ds = dirs_in("/usr")
    assert ds.count(Path("/usr/local")) > 0
    assert ds.count(Path("/usr/lib")) > 0


def test_name_with_parents() -> None:
    assert name_with_parents("bin", 1) == Null
    assert name_with_parents("/bin/ls", 1) == Some("bin_ls")
    assert name_with_parents("/bin/ls", 4) == Null
    assert name_with_parents("/bin/ls/1", 3) == Some("/_bin_ls_1")


def file_ctime_test() -> None:
    src_dir = "/var/ias/snapshot/shdt/n1/work/网络摔倒样本"
    dst_dir = "/var/ias/snapshot/shdt/n1/work/"
    ext = ".jpg"
    files = files_in(src_dir, ext)
    for src in files:
        t = file_mtime(src)

        dst = Path(dst_dir) / time_to_file(t, ext)
        print(src.name, " -> ", dst.name)
        dst.parent.mkdir(exist_ok=True)
        shutil.copy(src, dst)


def remove_parent_prefix_test() -> None:
    p = "/a/1.json"
    p1 = "/a/a_1.json"
    p2 = remove_parent_prefix(p1).unwrap()
    assert str(p2) == p

    p3 = remove_parent_prefix(p)
    assert p3.is_err()


def find_descendants_test() -> None:
    ds = find_descendants("/home/jiang", "b*", 2)
    for f in ds:
        print(f)


def test_last() -> None:
    f = "a/b/c.jpg"
    assert last_parts(f, 2) == Path("b/c.jpg")


def test_du() -> None:
    s = du(Path.home() / "bin")
    assert s > 1000000


def test_insert_dir() -> None:
    dir1 = tempfile.mkdtemp()
    bc = Path(dir1, "b", "c")
    bc.mkdir(parents=True, exist_ok=True)
    assert bc.is_dir()

    insert_dir(dir1, "a")
    abc = Path(dir1, "a", "b", "c")
    assert not bc.is_dir()
    assert abc.is_dir()

    shutil.rmtree(dir1)
