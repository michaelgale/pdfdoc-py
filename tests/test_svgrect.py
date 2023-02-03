# Sample Test passing with nose and pytest

import os
import sys
import pytest

from toolbox import *
from pdfdoc import *
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


def test_svgrect_render():
    c = canvas.Canvas(
        "./testfiles/test_svgrect.pdf", pagesize=(8.5 * inch, 11.0 * inch)
    )
    c.saveState()
    style_dict = {
        "top-margin": 0.05 * inch,
        "bottom-margin": 0.1 * inch,
        "left-margin": 0.1 * inch,
        "right-margin": 0.05 * inch,
        "horz-align": "centre",
        "vert-align": "centre",
    }

    cr = SvgRect(2 * inch, 1 * inch, "./testfiles/LogoBlackVector.svg")
    cr.show_debug_rects = True
    cr.style.set_with_dict(style_dict)
    cr.top_left = 1 * inch, 10 * inch
    cr.draw_in_canvas(c)

    cr = SvgRect(1 * inch, 2 * inch, "./testfiles/LogoBlackVector.svg")
    cr.show_debug_rects = True
    cr.style.set_with_dict(style_dict)
    cr.top_left = 4 * inch, 10 * inch
    cr.draw_in_canvas(c)

    cr = SvgRect(2 * inch, 2 * inch, "./testfiles/PFxLogoVector.svg")
    cr.show_debug_rects = True
    cr.style.set_with_dict(style_dict)
    cr.centre = 3 * inch, 5 * inch
    cr.draw_in_canvas(c)

    c.showPage()
    c.save()
