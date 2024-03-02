# Sample Test passing with nose and pytest

import os
import sys
import pytest

from toolbox import *
from pdfdoc import *
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


def test_alignmentrect_render():
    c = canvas.Canvas(
        "./tests/testfiles/test_alignmentrect.pdf", pagesize=(8.5 * inch, 11.0 * inch)
    )
    c.saveState()
    cr = PatternRect(3.25 * inch, 0.25 * inch)

    ar = AlignmentRect(6 * inch, 2 * inch)
    ar.style.set_with_dict(
        {
            "top-margin": 0.05 * inch,
            "bottom-margin": 0.1 * inch,
            "left-margin": 0.1 * inch,
            "right-margin": 0.05 * inch,
            "horz-align": "centre",
            "vert-align": "centre",
        }
    )
    ar.content = cr
    ar.show_debug_rects = True
    ar.rect.move_top_left_to(Point(1 * inch, 8 * inch))
    ar.draw_in_canvas(c)

    c.showPage()
    c.save()


def test_alignmentrect_placement():
    c = canvas.Canvas(
        "./tests/testfiles/test_alignmentrect2.pdf", pagesize=(8.5 * inch, 11.0 * inch)
    )
    cr = ContentRect(32, 32)
    cr.background_colour = "#402080"
    ar = AlignmentRect(2.5 * inch, 1.5 * inch)
    ar.style.set_with_dict(
        {
            "horz-align": "centre",
            "vert-align": "centre",
        }
    )
    ar.content = cr
    ar.show_debug_rects = True
    ar.rect.move_top_left_to(Point(1 * inch, 8 * inch))
    ar.draw_in_canvas(c)
    ar.horz_align = "left"
    ar.rect.move_top_left_to(Point(1 * inch, 6 * inch))
    ar.draw_in_canvas(c)
    ar.vert_align = "bottom"
    ar.rect.move_top_left_to(Point(1 * inch, 4 * inch))
    ar.draw_in_canvas(c)

    xr = ContentRect(32, 1.75 * inch)
    xr.background_colour = "#802040"

    tr = TextRect(32, 32, "1x")
    tr.font_size = 14
    tr.font_colour = "#FFFFFF"

    xr.overlay_content = tr
    ar.content = xr
    ar.horz_align = "centre"
    ar.vert_align = "top"
    ar.rect.move_top_left_to(Point(4 * inch, 8 * inch))
    ar.draw_in_canvas(c)
    ar.horz_align = "left"
    ar.rect.move_top_left_to(Point(4 * inch, 6 * inch))
    ar.draw_in_canvas(c)
    ar.horz_align = "right"
    ar.vert_align = "bottom"
    ar.rect.move_top_left_to(Point(4 * inch, 4 * inch))
    ar.draw_in_canvas(c)

    c.showPage()
    c.save()
