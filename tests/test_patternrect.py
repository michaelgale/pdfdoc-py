# Sample Test passing with nose and pytest

import os
import sys
import pytest

from fxgeometry import Point
from pdfdoc.patternrect import PatternRect
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

# _test_dict = {"left-margin": 2, "right-margin": 3, "horz-align": "left"}


# def test_textrect_init():
#     t1 = TextRect(10, 2, "MyText")
#     assert t1.rect.left == -5
#     assert t1.rect.right == 5
#     assert t1.rect.top == 1
#     assert t1.rect.bottom == -1


# def test_textrect_pos():
#     t1 = TextRect(10, 2, "MyText", _test_dict)
#     r1 = t1.style.get_inset_rect(t1.rect)
#     assert r1.left == -3
#     assert r1.right == 2
#     r1.move_top_left_to(Point(20, 50))
#     assert r1.left == 20
#     assert r1.right == 25
#     assert r1.top == 50
#     assert r1.bottom == 48
#     t1.style.set_all_margins(0.1)
#     r2 = t1.style.get_margin_rect(t1.rect)
#     assert r2.left == -4.9
#     assert r2.right == 4.9
#     assert r2.top == 0.9
#     assert r2.bottom == -0.9


_text_dict = {
    "border-outline": True,
    "border-width": 0.1 * inch,
    "border-colour": (1.0, 0.1, 0.2),
    "top-margin": 0.25 * inch,
    "bottom-margin": 0.025 * inch,
    "left-margin": 0.5 * inch,
    "right-margin": 0.05 * inch,
    "top-padding": 0.1 * inch,
    "bottom-padding": 0.2 * inch,
    "left-padding": 0.25 * inch,
    "right-padding": 0.5 * inch,
}


def test_patternrect_render():
    c = canvas.Canvas("test_patternrect.pdf", pagesize=(8.5 * inch, 11.0 * inch))
    c.saveState()
    t1 = PatternRect(3.25 * inch, 0.25 * inch)
    t1.show_debug_rects = True
    t1.rect.move_top_left_to(Point(1 * inch, 8 * inch))
    t1.draw_in_canvas(c)
    t2 = PatternRect(5 * inch, 0.5 * inch)
    t2.show_debug_rects = True
    t2.pattern = "squares"
    t2.pattern_width = 8
    t2.rect.move_top_left_to(Point(1 * inch, 7 * inch))
    t2.draw_in_canvas(c)

    c.showPage()
    c.save()
