# Sample Test passing with nose and pytest

import os
import sys
import pytest

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from toolbox import *
from pdfdoc import *


def test_table_text_array():
    c = canvas.Canvas(
        "./tests/testfiles/test_table_textarray.pdf", pagesize=(8.5 * inch, 11.0 * inch)
    )
    a1 = [
        "This is row 1",
        "This is row 2 (hopefully)",
        ["This is part of row 3", "And so is this"],
        "This is the last row",
        TextRect(icon="mandatory", font_size=56, font_colour="#4010F0"),
        SafetyLabel("warning_icon", "Warning", size=42),
        SafetyLabel("mandatory_icon", "This is an instruction"),
        SafetyLabel("mandatory_icon", "You must do this thing"),
        SafetyLabel("warning_icon", "This is a warning", size=32),
        SafetyLabel("icon_prohibited", "Do not do this"),
    ]
    s1 = DocStyle()
    s1.background_colour = "#EEC0FF"
    s1.background_fill = True
    s1.border_outline = True
    s1.border_colour = "#000000"
    s1.border_radius = 8
    e1 = DocStyle()
    e1.font = "DIN-Bold"
    e1.font_size = 14
    e1.font_colour = "#FFFFFF"
    e1.background_colour = "#4010F0"
    e1.background_fill = True
    e1.border_radius = 6
    e1.horz_align = "left"
    e1.left_padding = 12
    e1.vert_align = "top"
    e1.top_margin = 4
    e1.bottom_margin = 4
    e1.top_padding = 4
    t1 = TableVector.from_array(a1, style=s1, element_style=e1, fit_to_contents=True)
    t1.size = 5 * inch, 8 * inch
    t1.top_left = 1 * inch, 10 * inch
    t1.show_debug_rects = True
    t1.draw_in_canvas(c)
    c.showPage()
    c.save()


def test_table_from_array():
    c = canvas.Canvas(
        "./tests/testfiles/test_table_mixedarray.pdf",
        pagesize=(8.5 * inch, 11.0 * inch),
    )
    a1 = [
        TextRect("This is row 1"),
        ImageRect(1 * inch, 2 * inch, "./tests/testfiles/long.png"),
        [
            "This is part of row 3",
            SvgRect.from_preset("prohibited_touch", w=120, h=120),
        ],
        "And this is the next row which is longer",
        "This is the last row",
    ]

    s1 = DocStyle()
    s1.background_colour = "#FFEEC0"
    s1.background_fill = True
    s1.border_outline = True
    s1.border_colour = "#000000"
    s1.border_radius = 8
    s1.border_width = 4

    e1 = DocStyle(style={"font": "DIN-Bold", "font-size": 14, "horz-align": "left"})
    e1.set_all_padding(10)

    t1 = TableVector.from_array(a1, style=s1, element_style=e1, fit_to_contents=True)
    t1.size = 5 * inch, 3 * inch
    t1.top_left = 1 * inch, 10 * inch
    t1.show_debug_rects = True
    t1.draw_in_canvas(c)

    t1 = TableVector.from_array(a1, style=s1, element_style=e1, fit_to_contents=False)
    t1.size = 5 * inch, 3 * inch
    t1.top_left = 1 * inch, 5.5 * inch
    t1.show_debug_rects = True
    t1.draw_in_canvas(c)

    c.showPage()
    c.save()
