# Sample Test passing with nose and pytest

import os
import sys
import pytest

from pdfdoc.docstyle import DocStyle

_test_dict = {"left-margin": 2, "right-margin": 3, "horz-align": "left"}


def test_docstyle_attr():
    s1 = DocStyle()
    a1 = s1.get_attr("nonexistant")
    assert a1 is None
    a1 = s1.get_attr("nonexistant", 7)
    assert a1 == 7
    a2 = s1.get_attr("top-margin")
    assert a2 == 0
    a2 = s1.get_attr("top-margin", 3)
    assert a2 == 0


def test_docstyle_setattr():
    s1 = DocStyle()
    s1.set_with_dict(_test_dict)
    assert s1.get_attr("left-margin") == 2
    assert s1.get_attr("right-margin") == 3
    assert s1.get_attr("horz-align") == "left"
    assert s1.get_attr("horizontal-align") == "left"
    assert s1.get_attr("horizontal_align") == "left"
    assert s1.get_width_trim() == 5
    s1.set_attr("left-padding", 10)
    s1.set_attr("right-padding", 5)
    assert s1.get_left_trim() == 12
    assert s1.get_right_trim() == 8
    assert s1.get_width_trim() == 20
    assert s1.get_height_trim() == 0
