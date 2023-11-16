from jcx.text.io import *


def test_replace_in_file():
    txt1 = '1aa\na1a\naa1\n'
    txt2 = 'aaa\naaa\naaa\n'

    f = '/tmp/replace_in_file_test.txt'
    save_txt(txt1, f)
    replace_in_file(f, '1', 'a')

    s = load_txt(f).unwrap()
    assert s == txt2
