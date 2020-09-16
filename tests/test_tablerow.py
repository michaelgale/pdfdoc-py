# Sample Test passing with nose and pytest

import os
import sys
import pytest

from fxgeometry import Point
from pdfdoc.textrect import TextRect
from pdfdoc.tablerow import TableRow
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

_test_dict = {"left-margin": 1 * inch, "right-margin": 1 * inch, "horz-align": "left"}


def test_tablerow_init():
    tr = TableRow(6, 1, _test_dict)
    assert tr.rect.left == -3
    assert tr.rect.right == 3
    assert tr.rect.top == 0.5
    assert tr.rect.bottom == -0.5


_text_dict = {
    "border-outline": True,
    "border-width": 0.02 * inch,
    "border-colour": (1.0, 0.1, 0.2),
    "top-padding": 0.05 * inch,
    "bottom-padding": 0.05 * inch,
    "left-padding": 0.05 * inch,
    "right-padding": 0.05 * inch,
}


def test_tablerow_col():
    tr = TableRow(6 * inch, 1 * inch)
    tr.style.set_with_dict(
        {
            "top-margin": 0.05 * inch,
            "bottom-margin": 0.1 * inch,
            "left-margin": 0.5 * inch,
            "right-margin": 0.05 * inch,
        }
    )
    tr.style.set_tb_padding(0.1 * inch)
    t1 = TextRect(0, 0, "Column 1", _text_dict)
    t1.show_debug_rects = False
    t2 = TextRect(0, 0, "Column 2", _text_dict)
    t2.show_debug_rects = False
    t3 = TextRect(0, 0, "Column 3", _text_dict)
    t3.show_debug_rects = True
    tr.add_column("Col 1", t1)
    tr.add_column("Col 2", t2)
    tr.add_column("Col 3", t3)
    assert len(tr) == 3
    assert tr.cells[0].label == "Col 1"
    assert tr.cells[1].label == "Col 2"
    assert tr.cells[2].label == "Col 3"
    c = canvas.Canvas("test_tablerow.pdf", pagesize=(8.5 * inch, 11.0 * inch))
    c.saveState()
    tr.rect.move_top_left_to(Point(1 * inch, 9 * inch))
    tr.set_column_width("Col 1", 0.5)
    tr.style.set_attr("border-line-bottom", True)
    tr.style.set_attr("border-colour", (0.1, 0.1, 0.1))
    tr.style.set_attr("border-width", 0.02 * inch)
    tr.draw_in_canvas(c)

    tr.set_column_order("Col 1", 3)
    tr.rect.set_size(6.5 * inch, 0.75 * inch)
    tr.rect.move_top_left_to(Point(1 * inch, 7.5 * inch))
    tr.style.set_attr("background-fill", True)
    tr.style.set_attr("background-colour", (0.2, 0.8, 0.9))
    tr.style.set_attr("border-radius", 0.1 * inch)
    tr.draw_in_canvas(c)

    c.showPage()
    c.save()
