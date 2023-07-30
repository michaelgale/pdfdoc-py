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

    cr = SvgRect(1 * inch, 1 * inch, "./testfiles/NewRotationIcon.svg")
    cr.border_outline = True
    cr.border_width = 0.03 * inch
    cr.border_colour = (0, 0, 0)
    cr.style["border-radius"] = 0.175 * inch
    cr.style.set_all_padding(0.075 * inch)
    cr.top_left = 4 * inch, 10 * inch
    cr.draw_in_canvas(c)

    cr = SvgRect(2 * inch, 2 * inch, "./testfiles/PFxLogoVector.svg")
    cr.show_debug_rects = True
    cr.style.set_with_dict(style_dict)
    cr.centre = 3 * inch, 5 * inch
    cr.draw_in_canvas(c)

    c.showPage()
    c.save()


def test_preset():
    c = canvas.Canvas(
        "./testfiles/test_svg_preset.pdf", pagesize=(8.5 * inch, 11.0 * inch)
    )
    style_dict = {
        "top-margin": 0.05 * inch,
        "bottom-margin": 0.1 * inch,
        "left-margin": 0.1 * inch,
        "right-margin": 0.05 * inch,
        "horz-align": "centre",
        "vert-align": "centre",
    }

    cr = SvgRect.from_preset("warning_icon", style=style_dict)
    cr.size = 2 * inch, 2 * inch
    cr.show_debug_rects = True
    cr.top_left = 1 * inch, 10 * inch
    cr.draw_in_canvas(c)

    cr = SvgRect.from_preset(
        "no_touch_icon", w=90, h=90, top_left=(5 * inch, 10 * inch)
    )
    cr.show_debug_rects = True
    cr.draw_in_canvas(c)

    c.showPage()
    c.save()