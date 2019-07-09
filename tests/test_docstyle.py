# Sample Test passing with nose and pytest

import os
import sys
import pytest

from pdfdoc.docstyle import DocStyle

_test_dict = {
  "left-margin": 2,
  "right-margin": 3,
  "horz-align": "left",
}

def test_docstyle_attr():
    s1 = DocStyle()
    a1 = s1.get_attr("nonexistant")
    assert a1 is None
    a2 = s1.get_attr("top-margin")
    assert a2 == 0
    a2 = s1.get_attr("top-margin", 3)
    assert a2 == 3

def test_docstyle_setattr():
    s1 = DocStyle()
    s1.set_with_dict(_test_dict)
    assert s1.get_attr("left-margin") == 2
    assert s1.get_attr("right-margin") == 3
    assert s1.get_attr("horz-align") == "left"
    assert s1.get_attr("horizontal-align") == "left"
