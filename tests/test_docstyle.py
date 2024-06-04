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
    a3 = s1.top_margin
    assert a3 == 0
    assert s1["ncolumns"] == 0
    s1.columns = 3
    assert s1["ncolumns"] == 3
    assert s1["ncols"] == 3
    assert s1["columns"] == 3
    assert s1.columns == 3
    s1["ncolumns"] = 1
    assert s1.columns == 1


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
    assert s1.left_padding == 20
    s1.top_margin = 13
    assert s1.top_margin == 13
    assert s1["top-margin"] == 13
    assert s1["top_margin"] == 13


def test_set_yaml():
    yml1 = """
        font: "DIN-Bold"
        font-size: 14
        font-colour: "#FFFFFF"
        background-colour: "#202020"
        background-fill: True
        border-radius: 6
        horz_align: "left"
        vert-align: "top"
        left-padding: 8
        top-padding: 8
        """
    e1 = DocStyle.from_yaml(yml1)
    assert e1.font_size == 14
    assert e1.border_radius == 6
    assert e1.horz_align == "left"
    assert e1.vert_align == "top"
    assert e1.left_padding == 8
    assert e1.background_fill

    e2 = DocStyle(yml1)
    assert e2.font_size == 14
    assert e2.border_radius == 6
    assert e2.horz_align == "left"
    assert e2.vert_align == "top"
    assert e2.left_padding == 8
    assert e2.background_fill


def test_docstylesheet():
    styles = DocStyleSheet(filename="./tests/testfiles/sample_stylesheet.yml")
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
