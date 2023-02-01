# Sample Test passing with nose and pytest

import os
import sys
import pytest

from toolbox import *
from pdfdoc.textrect import TextRect
from pdfdoc.tablerow import TableRow
from pdfdoc import CMYKGrid
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


def test_cmykgrid():
    c = canvas.Canvas(
        "./testfiles/test_cmykgrid.pdf", pagesize=(8.5 * inch, 11.0 * inch)
    )
    cg = CMYKGrid(2 * inch, 2 * inch)
    cg.label_style.set_with_dict(
        {
            "font-size": 7,
            "border-width": 0.5,
        }
    )
    cg.top_left = 1 * inch, 10 * inch
    cg.draw_in_canvas(c)

    cg = CMYKGrid(2 * inch, 2 * inch, cols=9, col_channel="C")
    cg.top_left_cmyk = (0.02, 0, 0, 0)
    cg.label_style.set_with_dict(
        {
            "font-size": 7,
            "border-width": 0.5,
        }
    )
    cg.set_col_range((0.1, 0.4))
    cg.top_left = 3.5 * inch, 10 * inch
    cg.draw_in_canvas(c)

    cg = CMYKGrid(
        2 * inch,
        2 * inch,
        rows=9,
        row_channel="M",
        col_channel="Y",
        labels=False,
        padding=0.5,
    )
    cg.top_left_cmyk = (0.04, 0, 0, 0)
    cg.set_row_range(0.6, 0.2)
    cg.label_style.set_with_dict(
        {
            "font-size": 7,
            "border-width": 0.5,
        }
    )
    cg.top_left = 6 * inch, 10 * inch
    cg.draw_in_canvas(c)

    cg = CMYKGrid()
    cg.label_style.set_with_dict(
        {
            "font-size": 7,
            "border-width": 0.5,
        }
    )
    cg.labels_in_pct = False
    cg.row_channel = "C"
    cg.row_inc = 0.05
    cg.rows = 12
    cg.col_channel = "K"
    cg.col_inc = 0.04
    cg.cols = 16
    cg.set_centre_cmyk((0.5, 0.25, 0.15, 0.3))
    cg.padding = 0.5
    cg.size = 4 * inch, 4 * inch
    cg.top_left = 2 * inch, 6 * inch
    cg.draw_in_canvas(c)

    c.showPage()
    c.save()
