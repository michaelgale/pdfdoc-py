# Sample Test passing with nose and pytest

import os
import sys
import pytest

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from toolbox import *
from pdfdoc import *

_test_dict = {"left-margin": 1 * inch, "right-margin": 1 * inch, "horz-align": "left"}


def test_tablecolumn_init():
    tr = TableColumn(1, 6, _test_dict)
    assert tr.rect.left == -0.5
    assert tr.rect.right == 0.5
    assert tr.rect.top == 3
    assert tr.rect.bottom == -3


_text_dict = {
    "border-outline": True,
    "border-width": 0.02 * inch,
    "border-colour": (1.0, 0.1, 0.2),
    "top-padding": 0.05 * inch,
    "bottom-padding": 0.05 * inch,
    "left-padding": 0.05 * inch,
    "right-padding": 0.05 * inch,
}


def test_tablecolumn_row():
    tr = TableColumn(1 * inch, 6 * inch)
    tr.style.set_with_dict(
        {
            "top-margin": 0.5 * inch,
            "bottom-margin": 0.1 * inch,
            "left-margin": 0.05 * inch,
            "right-margin": 0.05 * inch,
        }
    )
    tr.style.set_tb_padding(0.1 * inch)
    t1 = TextRect(0, 0, "R 1", _text_dict)
    t1.show_debug_rects = False
    t2 = TextRect(0, 0, "R 2", _text_dict)
    t2.show_debug_rects = False
    t3 = TextRect(0, 0, "R 3", _text_dict)
    t3.show_debug_rects = True
    tr.add_row("Row 1", t1)
    tr.add_row("Row 2", t2)
    tr.add_row("Row 3", t3)
    assert len(tr) == 3
    assert tr.cells[0].label == "Row 1"
    assert tr.cells[1].label == "Row 2"
    assert tr.cells[2].label == "Row 3"
    c = canvas.Canvas(
        "./tests/testfiles/test_tablecolumn.pdf", pagesize=(8.5 * inch, 11.0 * inch)
    )
    c.saveState()
    tr.rect.move_top_left_to(Point(1 * inch, 9 * inch))
    tr.set_row_height("Row 1", 0.5)
    tr.style["border-line-bottom"] = True
    tr.style["border-colour"] = (0.1, 0.1, 0.1)
    tr.style["border-width"] = 0.02 * inch
    tr.draw_in_canvas(c)

    tr.set_row_order("Row 1", 3)
    tr.rect.set_size(2.0 * inch, 6.5 * inch)
    tr.rect.move_top_left_to(Point(4 * inch, 8 * inch))
    tr.draw_in_canvas(c)

    c.showPage()
    c.save()


def test_tableimbedded():
    tr = TableColumn(4 * inch, 6 * inch)
    tr.style.set_with_dict(
        {
            "top-margin": 0.5 * inch,
            "bottom-margin": 0.1 * inch,
            "left-margin": 0.05 * inch,
            "right-margin": 0.05 * inch,
        }
    )
    tr.style.set_tb_padding(0.1 * inch)
    t1 = TableRow(3 * inch, 2.75 * inch)
    t1a = TextRect(0, 0, "C1", _text_dict)
    t1a.style.set_all_margins(0.1 * inch)
    t1b = TextRect(0, 0, "C2", _text_dict)
    t1c = TextRect(0, 0, "C3", _text_dict)
    t1.add_column("Col 1", t1a)
    t1.add_column("Col 2", t1b)
    t1.add_column("Col 3", t1c)

    t2 = TextRect(0, 0, "R 2", _text_dict)
    t2.show_debug_rects = False
    t3 = TextRect(0, 0, "R 3", _text_dict)
    t3.show_debug_rects = True
    tr.add_row("Row 1", t1)
    tr.add_row("Row 2", t2)
    tr.add_row("Row 3", t3)
    tr.set_row_height("Row 1", 0.5)
    assert len(tr) == 3

    c = canvas.Canvas(
        "./tests/testfiles/test_tableimbed.pdf", pagesize=(8.5 * inch, 11.0 * inch)
    )
    c.saveState()
    tr.top_left = Point(1 * inch, 9 * inch)
    tr.border_outline = "bottom"
    tr.border_colour = (0.1, 0.1, 0.1)
    tr.border_width = 0.02 * inch
    tr.draw_in_canvas(c)
    c.showPage()
    c.save()
