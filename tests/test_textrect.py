# Sample Test passing with nose and pytest

import os
import sys
import pytest

from toolbox import *
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from pdfdoc import *

_test_dict = {"left-margin": 2, "right-margin": 3, "horz-align": "left"}


def test_textrect_init():
    t1 = TextRect(10, 2, "MyText")
    assert t1.rect.left == -5
    assert t1.rect.right == 5
    assert t1.rect.top == 1
    assert t1.rect.bottom == -1

    assert t1.size == (10, 2)
    t1.size = (20, 3)
    assert t1.size == (20, 3)

    t2 = TextRect()
    assert t2.clip_text == False
    t3 = TextRect(clip_text=True)
    assert t3.clip_text == True


def test_textrect_pos():
    t1 = TextRect(10, 2, "MyText", _test_dict)
    r1 = t1.style.get_inset_rect(t1.rect)
    assert r1.left == -3
    assert r1.right == 2
    r1.move_top_left_to(Point(20, 50))
    assert r1.left == 20
    assert r1.right == 25
    assert r1.top == 50
    assert r1.bottom == 48

    assert t1.top_left == (-5, 1)
    t1.top_left = (3, 20)
    assert t1.top_left == (3, 20)
    t1.top_left = (-5, 1)

    t1.style.set_all_margins(0.1)
    r2 = t1.style.get_margin_rect(t1.rect)
    assert r2.left == -4.9
    assert r2.right == 4.9
    assert r2.top == 0.9
    assert r2.bottom == -0.9


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


test_para = (
    "This is a very long string of words which will hopefully split over a few lines"
)


def test_string_splitting():
    t1 = TextRect(4 * inch, 1.5 * inch, test_para, _text_dict)
    c = canvas.Canvas(
        "./testfiles/test_splitlines.pdf", pagesize=(8.5 * inch, 11.0 * inch)
    )
    c.saveState()
    t1.split_lines = True
    t1.show_debug_rects = True
    t1.horz_align = "left"
    t1.vert_align = "top"
    t1.top_left = 1 * inch, 9 * inch
    t1.draw_in_canvas(c)

    t1.horz_align = "left"
    t1.vert_align = "bottom"
    t1.top_left = 1 * inch, 7 * inch
    t1.draw_in_canvas(c)

    t1.horz_align = "left"
    t1.vert_align = "centre"
    t1.top_left = 1 * inch, 5 * inch
    t1.draw_in_canvas(c)

    t1.horz_align = "left"
    t1.vert_align = "centre"
    t1.top_left = 1 * inch, 3 * inch
    t1.split_lines = False
    t1.scale_to_fit = True
    t1.draw_in_canvas(c)

    c.showPage()
    c.save()


def test_textrect_render():
    c = canvas.Canvas(
        "./testfiles/test_textrect.pdf", pagesize=(8.5 * inch, 11.0 * inch)
    )
    c.saveState()
    t1 = TextRect(3 * inch, 1 * inch, "My Centre Test", _text_dict)
    t1.show_debug_rects = True
    t1.vert_align = "centre"
    t1.top_left = 1 * inch, 8 * inch
    t1.draw_in_canvas(c)

    t2 = TextRect(3 * inch, 1 * inch, "My Top Test", _text_dict)
    t2.show_debug_rects = True
    t2.vert_align = "top"
    t2.top_left = 1 * inch, 6.5 * inch
    t2.draw_in_canvas(c)

    t3 = TextRect(3 * inch, 1 * inch, "My Bottom Test", _text_dict)
    t3.show_debug_rects = True
    t3.vert_align = "bottom"
    t3.top_left = 1 * inch, 5 * inch
    t3.draw_in_canvas(c)

    t1 = TextRect(3 * inch, 1 * inch, "My Left Test", _text_dict)
    t1.show_debug_rects = True
    t1.horz_align = "left"
    t1.vert_align = "centre"
    t1.top_left = 4.5 * inch, 8 * inch
    t1.draw_in_canvas(c)

    t2 = TextRect(3 * inch, 1 * inch, "My Centre Test", _text_dict)
    t2.show_debug_rects = True
    t2.horz_align = "centre"
    t2.vert_align = "centre"
    t2.top_left = 4.5 * inch, 6.5 * inch
    t2.draw_in_canvas(c)

    t3 = TextRect(3 * inch, 1 * inch, "My Right Test", _text_dict)
    t3.show_debug_rects = True
    t3.horz_align = "right"
    t3.vert_align = "centre"
    t3.top_left = 4.5 * inch, 5 * inch
    t3.draw_in_canvas(c)

    c.showPage()
    c.save()
