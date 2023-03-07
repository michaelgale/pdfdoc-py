# Sample Test passing with nose and pytest

import os
import sys
import pytest

from toolbox import *
from pdfdoc import *
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


def test_fixedrect():
    c = canvas.Canvas(
        "./testfiles/test_fixedrect.pdf", pagesize=(8.5 * inch, 11.0 * inch)
    )
    c.saveState()
    cr = FixedRect(1 * inch, 1 * inch)
    cr.show_debug_rects = True
    cr.rect.move_top_left_to(Point(1 * inch, 8 * inch))
    cr.draw_in_canvas(c)

    cr2 = FixedRect(0.75 * inch, 0.5 * inch)
    cr2.style.set_with_dict(
        {
            "border-outline": True,
            "border-width": 0.025 * inch,
            "border-colour": "#402080",
            "border-radius": 0.1 * inch,
        }
    )
    cr2.show_debug_rects = True
    cr2.rect.move_top_left_to(Point(2 * inch, 5 * inch))
    cr2.draw_in_canvas(c)

    c.showPage()
    c.save()
