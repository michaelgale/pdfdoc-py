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
        "./testfiles/test_alignmentrect.pdf", pagesize=(8.5 * inch, 11.0 * inch)
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
