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
    tr.vert_align = "bottom"
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
    tr.top_left = Point(1 * inch, 9 * inch)
    assert tr.top_left == (1 * inch, 9 * inch)
    tr.draw_in_canvas(c)

    r = ContentRect(5 * inch, 3 * inch)
    r.show_debug_rects = True
    r.top_left = Point(1 * inch, 9 * inch)
    r.draw_in_canvas(c)
    c.showPage()
    c.save()


def test_tablegrid_cols():
    NUM_ITEMS = 22
    TABLE_WIDTH = 3.5 * inch
    TABLE_HEIGHT = 6.5 * inch
    titles = [
        "TableCell-%d" % (x)
        if x % 2 == 0
        else "%d-%s" % (x, str(x) * random.randint(1, 8))
        for x in range(NUM_ITEMS)
    ]
    top_pads = [random.randint(0, 10) * 0.02 * inch for _ in range(NUM_ITEMS)]
    bot_pads = [random.randint(0, 10) * 0.02 * inch for _ in range(NUM_ITEMS)]

    def tablegrid_col_test(fn, title, opts):
        tr = TableGrid(TABLE_WIDTH, TABLE_HEIGHT)
        tr.fill_dir = "column-wise"
        tr.horz_align = "left"
        tr.vert_align = "bottom"
        tr.align_cols = False
        tr.style.set_with_dict(
            {
                "top-margin": 0.05 * inch,
                "bottom-margin": 0.1 * inch,
                "left-margin": 0.1 * inch,
                "right-margin": 0.05 * inch,
                "gutter-line": 0.03 * inch,
                "gutter-width": 0.25 * inch,
            }
        )
        tr.style.set_tb_padding(0.05 * inch)

        for x in range(NUM_ITEMS):
            cl = titles[x]
            if x == 0:
                cl = title
            tc = TextRect(0, 0, cl, _text_dict)
            tc.show_debug_rects = True
            tc.style.set_attr("top-padding", top_pads[x])
            tc.style.set_attr("bottom-padding", bot_pads[x])
            tr.add_cell(cl, tc)

        assert len(tr) == NUM_ITEMS
        tr.layout_opts = opts
        c = canvas.Canvas(fn, pagesize=(8.5 * inch, 11.0 * inch))
        c.saveState()
        tr.top_left = Point(1 * inch, 9 * inch)
        tr.draw_in_canvas(c)

        r = ContentRect(TABLE_WIDTH, TABLE_HEIGHT)
        r.show_debug_rects = True
        r.top_left = Point(1 * inch, 9 * inch)
        r.draw_in_canvas(c)
        c.showPage()

        c.save()

    tablegrid_col_test(
        "./testfiles/test_tablegrid_cols.pdf", "Normal", {"strategy": "none"}
    )
    tablegrid_col_test(
        "./testfiles/test_tablegrid_cols_1.pdf",
        "Resize",
        {
            "strategy": "resize",
            "whitespace_thr": 0.20,
        },
    )
    tablegrid_col_test(
        "./testfiles/test_tablegrid_cols_2.pdf",
        "Whitspc",
        {
            "strategy": "reshape",
            "whitespace_weight": 1.0,
            "distortion_weight": 0.0,
            "full_reshape": False,
        },
    )
    tablegrid_col_test(
        "./testfiles/test_tablegrid_cols_3.pdf",
        "Distort",
        {
            "strategy": "reshape",
            "whitespace_weight": 0.5,
            "distortion_weight": 1.0,
            "full_reshape": False,
        },
    )
    tablegrid_col_test(
        "./testfiles/test_tablegrid_cols_4.pdf",
        "Balance",
        {
            "strategy": "reshape",
            "whitespace_weight": 1.0,
            "distortion_weight": 1.0,
            "full_reshape": False,
        },
    )


def test_tablegrid_gutters():
    NUM_ITEMS = 6
    TABLE_WIDTH = 6.5 * inch
    TABLE_HEIGHT = 1.5 * inch
    titles = [
        "TableCell-%d" % (x)
        if x % 2 == 0
        else "%d-%s" % (x, str(x) * random.randint(1, 8))
        for x in range(NUM_ITEMS)
    ]
    top_pads = [random.randint(2, 10) * 0.03 * inch for _ in range(NUM_ITEMS)]
    bot_pads = [random.randint(2, 10) * 0.03 * inch for _ in range(NUM_ITEMS)]

    def tablegrid_col_test(fn, title, opts):
        tr = TableGrid(TABLE_WIDTH, TABLE_HEIGHT)
        tr.fill_dir = "column-wise"
        tr.horz_align = "left"
        tr.vert_align = "bottom"
        tr.align_cols = False
        tr.style.set_with_dict(
            {
                "top-margin": 0.05 * inch,
                "bottom-margin": 0.1 * inch,
                "left-margin": 0.1 * inch,
                "right-margin": 0.05 * inch,
                "gutter-line": 0.03 * inch,
                "gutter-width": 0.15 * inch,
            }
        )
        tr.style.set_tb_padding(0.05 * inch)

        for x in range(NUM_ITEMS):
            cl = titles[x]
            if x == 0:
                cl = title
            tc = TextRect(0, 0, cl, _text_dict)
            tc.show_debug_rects = True
            tc.style.set_attr("top-padding", top_pads[x])
            tc.style.set_attr("bottom-padding", bot_pads[x])
            tr.add_cell(cl, tc)

        assert len(tr) == NUM_ITEMS
        tr.layout_opts = opts
        c = canvas.Canvas(fn, pagesize=(8.5 * inch, 11.0 * inch))
        c.saveState()
        tr.top_left = Point(1 * inch, 9 * inch)
        tr.draw_in_canvas(c)

        r = ContentRect(TABLE_WIDTH, TABLE_HEIGHT)
        r.show_debug_rects = True
        r.top_left = Point(1 * inch, 9 * inch)
        r.draw_in_canvas(c)
        c.showPage()

        c.save()

    tablegrid_col_test(
        "./testfiles/test_tablegrid_gutters.pdf", "Normal", {"strategy": "none"}
    )
