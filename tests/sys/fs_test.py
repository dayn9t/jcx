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


def test_file_stems_in() -> None:
    ds = file_stems_in("/etc/supervisor", ".conf")
    print(ds)


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
    s = du(Path.home() / ".local/bin")
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


class TestFileTimeIterator:
    """Tests for FileTimeIterator class."""

    def test_basic_iteration(self):
        """Test that iterator yields sequential paths."""
        from arrow import Arrow

        from jcx.sys.fs import FileTimeIterator

        start = Arrow(2026, 3, 21, 14, 30, 0)
        base = Path("/tmp/test")
        iterator = FileTimeIterator(base, start, ".jpg")

        path1 = next(iterator)
        path2 = next(iterator)
        path3 = next(iterator)

        # Check base path
        assert path1.parent == base
        assert path2.parent == base
        assert path3.parent == base

        # Check extension
        assert path1.suffix == ".jpg"
        assert path2.suffix == ".jpg"
        assert path3.suffix == ".jpg"

        # Check sequential timestamps (1 second apart)
        assert path1.stem != path2.stem
        assert path2.stem != path3.stem

    def test_timestamp_advances_one_second(self):
        """Test that each call advances timestamp by 1 second."""
        from arrow import Arrow

        from jcx.sys.fs import FileTimeIterator, time_to_file

        start = Arrow(2026, 3, 21, 14, 30, 0)
        base = Path("/tmp")
        iterator = FileTimeIterator(base, start, ".txt")

        # Get first path and extract timestamp
        path1 = next(iterator)
        expected_name1 = time_to_file(start, ".txt", date_dir=False)
        assert path1.name == expected_name1

        # Get second path - should be 1 second later
        path2 = next(iterator)
        expected_name2 = time_to_file(start.shift(seconds=1), ".txt", date_dir=False)
        assert path2.name == expected_name2

    def test_peek_does_not_advance(self):
        """Test that peek() returns current without advancing."""
        from arrow import Arrow

        from jcx.sys.fs import FileTimeIterator

        start = Arrow(2026, 3, 21, 14, 30, 0)
        base = Path("/tmp")
        iterator = FileTimeIterator(base, start, ".jpg")

        peeked = iterator.peek()
        actual = next(iterator)

        assert peeked == actual

        # After next(), peek should return the next one
        peeked2 = iterator.peek()
        actual2 = next(iterator)
        assert peeked2 == actual2

    def test_reset_changes_start_time(self):
        """Test that reset() changes the current time."""
        from arrow import Arrow

        from jcx.sys.fs import FileTimeIterator, time_to_file

        start1 = Arrow(2026, 3, 21, 14, 30, 0)
        start2 = Arrow(2026, 3, 22, 10, 0, 0)
        base = Path("/tmp")
        iterator = FileTimeIterator(base, start1, ".jpg")

        # Get first path
        path1 = next(iterator)

        # Reset to new time
        iterator.reset(start2)
        path2 = next(iterator)

        # Should use new start time
        expected_name2 = time_to_file(start2, ".jpg", date_dir=False)
        assert path2.name == expected_name2

    def test_multiple_iterators_independent(self):
        """Test that multiple iterators are independent."""
        from arrow import Arrow

        from jcx.sys.fs import FileTimeIterator

        start = Arrow(2026, 3, 21, 14, 30, 0)
        base = Path("/tmp")

        iter1 = FileTimeIterator(base, start, ".jpg")
        iter2 = FileTimeIterator(base, start.shift(hours=1), ".jpg")

        path1_from_iter1 = next(iter1)
        path1_from_iter2 = next(iter2)
        path2_from_iter1 = next(iter1)

        # Each iterator maintains its own state
        assert path1_from_iter1 != path1_from_iter2
        assert path2_from_iter1.name != path1_from_iter1.name

    def test_custom_extension(self):
        """Test iterator with different extensions."""
        from arrow import Arrow

        from jcx.sys.fs import FileTimeIterator

        start = Arrow(2026, 3, 21, 14, 30, 0)
        base = Path("/tmp")

        for ext in [".png", ".txt", ".mp4", ".csv"]:
            iterator = FileTimeIterator(base, start, ext)
            path = next(iterator)
            assert path.suffix == ext
