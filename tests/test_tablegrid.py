# Sample Test passing with nose and pytest

import os
import sys
import pytest
import random

from toolbox import *
from pdfdoc import *
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

_test_dict = {"left-margin": 1 * inch, "right-margin": 1 * inch, "horz-align": "left"}


_text_dict = {
    "border-outline": True,
    "border-width": 0.02 * inch,
    "border-colour": (1.0, 0.1, 0.2),
    "top-padding": 0.05 * inch,
    "bottom-padding": 0.05 * inch,
    "left-padding": 0.05 * inch,
    "right-padding": 0.05 * inch,
}


def test_tablegrid_rows():
    tr = TableGrid(5 * inch, 3 * inch)
    tr.fill_dir = "row-wise"
    tr.style.set_attr("vert-align", "bottom")
    tr.style.set_with_dict(
        {
            "top-margin": 0.05 * inch,
            "bottom-margin": 0.1 * inch,
            "left-margin": 0.1 * inch,
            "right-margin": 0.05 * inch,
        }
    )
    tr.style.set_tb_padding(0.1 * inch)

    for x in range(15):
        cl = "TableCell-%d" % (x) if x % 2 == 0 else "%d" % (x) * random.randint(1, 10)
        tc = TextRect(0, 0, cl, _text_dict)
        tp = random.randint(1, 10) * 0.025 * inch
        bp = random.randint(1, 10) * 0.025 * inch
        tc.style.set_attr("top-padding", tp)
        tc.style.set_attr("bottom-padding", bp)
        tc.show_debug_rects = True
        tr.add_cell(cl, tc)

    assert len(tr) == 15
    # assert tr.cells[0].label == "TableCell-0"
    # assert tr.cells[1].label == "Grid 1"
    # assert tr.cells[2].label == "TableCell-2"
    c = canvas.Canvas(
        "./testfiles/test_tablegrid_rows.pdf", pagesize=(8.5 * inch, 11.0 * inch)
    )
    c.saveState()

    tr.rect.move_top_left_to(Point(1 * inch, 9 * inch))
    tr.draw_in_canvas(c)

    r = ContentRect(5 * inch, 3 * inch)
    r.show_debug_rects = True
    r.rect.move_top_left_to(Point(1 * inch, 9 * inch))
    r.draw_in_canvas(c)
    c.showPage()
    c.save()


def test_tablegrid_cols():
    tr = TableGrid(5 * inch, 3 * inch)
    tr.fill_dir = "column-wise"
    tr.style.set_attr("horz-align", "left")
    tr.style.set_with_dict(
        {
            "top-margin": 0.05 * inch,
            "bottom-margin": 0.1 * inch,
            "left-margin": 0.1 * inch,
            "right-margin": 0.05 * inch,
        }
    )
    tr.style.set_tb_padding(0.1 * inch)

    for x in range(15):
        cl = "TableCell-%d" % (x) if x % 2 == 0 else "%d" % (x) * random.randint(1, 10)
        tc = TextRect(0, 0, cl, _text_dict)
        tc.show_debug_rects = True
        tp = random.randint(1, 10) * 0.008 * inch
        bp = random.randint(1, 10) * 0.008 * inch
        tc.style.set_attr("top-padding", tp)
        tc.style.set_attr("bottom-padding", bp)
        tr.add_cell(cl, tc)

    assert len(tr) == 15
    # assert tr.cells[0].label == "TableCell-0"
    # assert tr.cells[1].label == "Grid 1"
    # assert tr.cells[2].label == "TableCell-2"
    c = canvas.Canvas(
        "./testfiles/test_tablegrid_cols.pdf", pagesize=(8.5 * inch, 11.0 * inch)
    )
    c.saveState()
    tr.rect.move_top_left_to(Point(1 * inch, 9 * inch))
    tr.draw_in_canvas(c)

    r = ContentRect(5 * inch, 3 * inch)
    r.show_debug_rects = True
    r.rect.move_top_left_to(Point(1 * inch, 9 * inch))
    r.draw_in_canvas(c)
    c.showPage()
    c.save()
