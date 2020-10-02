# Sample Test passing with nose and pytest

import os
import sys
import pytest

from pdfdoc import *

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
    assert s1["left-margin"] == 2
    assert s1.get_attr("right-margin") == 3
    assert s1.get_attr("horz-align") == "left"
    assert s1["horizontal-align"] == "left"
    assert s1["horizontal_align"] == "left"
    assert s1["horz-align"] == "left"
    assert s1.get_width_trim() == 5
    s1.set_attr("left-padding", 10)
    s1.set_attr("right-padding", 5)
    assert s1.get_left_trim() == 12
    assert s1.get_right_trim() == 8
    assert s1.get_width_trim() == 20
    assert s1.get_height_trim() == 0
    s1["left-padding"] = 20
    assert s1["left-padding"] == 20


def test_docstylesheet():
    styles = DocStyleSheet(filename="./testfiles/sample_stylesheet.yml")
    assert "STEP_NUM_STYLE" in styles.styles
    assert "CALLOUT_STYLE_L1" in styles.styles
    assert "BLACK" not in styles.styles
    s1 = styles.get_style("PREVIEW_QTY_STYLE")
    assert s1.get_attr("font-name") == "IKEA-Sans-Regular"
    assert s1.get_attr("font-size") == 24
    assert s1.get_attr("font-colour") == (0.0, 0.0, 0.0)
    assert s1.get_attr("border-width") == 0
    assert s1.get_attr("vert-align") == "bottom"
    assert s1.get_attr("horz-align") != "top"
    
    styles.set_style("OTHER", _test_dict)
    assert "OTHER" in styles.styles
    s2 = styles.get_style("OTHER")
    assert s2.get_attr("right-margin") == 3

    s3 = DocStyle(style=_test_dict)
    styles.set_style("THISONE", s3)
    assert "THISONE" in styles.styles
    s4 = styles.get_style("THISONE")
    assert s4.get_attr("left-margin") == 2

    s5 = styles["STEP_NUM_STYLE"]
    assert s5.get_attr("font-size") == 32
