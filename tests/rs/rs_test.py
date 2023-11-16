from jcx.rs.rs import *


def test_rs_option():
    assert rs_option(None) == Null
    assert rs_option(1) == Some(1)


def test_py_optional():
    assert py_optional(Null) is None
    assert py_optional(Some(1)) == 1
