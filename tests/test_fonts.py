# Sample Test passing with nose and pytest

import os
import sys
import pytest

from toolbox import *
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from pdfdoc import *


def test_listfiles():
    # list_fonts("*.ttf")
    # list_fonts("*.otf")

    find_font("freesans")
    find_font("FuturaStd-Medium.otf")
    find_font("UKNumberPlate")
    find_font("uknumberplate")
    find_font("Transport Heavy")
    find_font("IKEA Sans Regular")


def test_font_specimen():
    create_specimen_pdf("DIN-Regular", "./testfiles/test_specimen.pdf")


_font_dict = {
    "font-name": "Avenir-0",
    "font-size": 18,
    "horz-align": "left",
}


def test_register_font():
    valid_fonts = register_font_family("/System/Library/Fonts/Avenir Next.ttc")
    c = canvas.Canvas(
        "./testfiles/test_fontnames.pdf", pagesize=(8.5 * inch, 11.0 * inch)
    )
    c.saveState()
    for i, font in enumerate(valid_fonts):
        _font_dict["font-name"] = font
        t1 = TextRect(
            4 * inch, 0.5 * inch, "%s Font Speciment" % (font), style=_font_dict
        )
        t1.rect.move_top_left_to(Point(1 * inch, 10 * inch - i * 0.5 * inch))
        t1.draw_in_canvas(c)
    c.showPage()
    c.save()
