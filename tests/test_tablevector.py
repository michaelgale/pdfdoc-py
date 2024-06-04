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
        "./tests/testfiles/test_table_textarray.pdf", pagesize=CANVAS_LETTER
    )
    a1 = [
        "This is row 1",
        "This is row 2 (hopefully)",
        ["This is part of row 3", "And so is this", "as well as this thing"],
        "This is the last row",
        TextRect(icon="mandatory", font_size=48, font_colour="#4010F0"),
        SafetyLabel("warning_icon", "Warning", size=42),
        SafetyLabel("mandatory_icon", "This instruction", size=42),
        SafetyLabel("icon_prohibited", "Do not do this", size=42),
        SafetyLabel("mandatory_icon", "You must do this thing"),
        SafetyLabel("warning_icon", "This is a warning", size=32, aspect_ratio=7),
    ]
    s1 = DocStyle.from_yaml(
        """
        background_colour: "#EEE0FF"
        background_fill: True
        border_outline: True
        border_width: 2
        border_colour: "#000000"
        border_radius: 8
        """
    )
    s1.set_all_padding(6)
    e1 = DocStyle.from_yaml(
        """
        font: DIN-Bold
        font-size: 14
        font-colour: "#FFFFFF"
        background-colour: "#202020"
        background-fill: True
        border-radius: 6
        horz-align: left
        vert-align: top
        left-padding: 8
        right-padding: 8
        top-padding: 8
        bottom-padding: 8
        """
    )
    t1 = TableVector.from_array(
        a1, style=s1, element_style=e1, fit_to_contents=True, element_margin=8
    )
    t1.size = 5 * inch, 8 * inch
    t1.top_left = 1 * inch, 10 * inch
    t1.show_debug_rects = True
    t1.draw_in_canvas(c)
    c.showPage()
    c.save()


def test_table_from_array():
    c = canvas.Canvas(
        "./tests/testfiles/test_table_mixedarray.pdf",
        pagesize=CANVAS_LETTER,
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

    s1 = DocStyle(
        {
            "background-colour": "#FFEEC0",
            "background-fill": True,
            "border-outline": True,
            "border-colour": "#000000",
            "border-radius": 8,
            "border-width": 4,
        }
    )

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
