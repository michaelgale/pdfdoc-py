# Sample Test passing with nose and pytest

import os
import sys
import pytest

from fxgeometry import Point
from pdfdoc.textrect import TextRect
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

_test_dict = {
  "left-margin": 2,
  "right-margin": 3,
  "horz-align": "left",
}

def test_textrect_init():
    t1 = TextRect(10, 2, "MyText")
    assert t1.rect.left == -5
    assert t1.rect.right == 5
    assert t1.rect.top == 1
    assert t1.rect.bottom == -1

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

_text_dict = {
  "border-outline": True,
  "border-width": 0.1 * inch,
  "border-colour": (1.0, 0.1, 0.2),
  "top-padding": 0.1 * inch,
  "bottom-padding": 0.2 * inch,
  "left-padding": 0.25 * inch,
  "right-padding": 0.5 * inch
}

def test_textrect_render():
    c = canvas.Canvas("test_textrect.pdf", pagesize=(8.5 * inch, 11.0 * inch))
    c.saveState()
    t1 = TextRect(3*inch, 1*inch, "My Centre Test", _text_dict)
    t1.show_debug_rects = True
    t1.style.set_attr("vert-align", "centre")
    t1.rect.move_top_left_to(Point(1*inch, 8*inch))
    t1.draw_in_canvas(c)

    t2 = TextRect(3*inch, 1*inch, "My Top Test", _text_dict)
    t2.show_debug_rects = True
    t2.style.set_attr("vert-align", "top")
    t2.rect.move_top_left_to(Point(1*inch, 6.5*inch))
    t2.draw_in_canvas(c)

    t3 = TextRect(3*inch, 1*inch, "My Bottom Test", _text_dict)
    t3.show_debug_rects = True
    t3.style.set_attr("vert-align", "bottom")
    t3.rect.move_top_left_to(Point(1*inch, 5*inch))
    t3.draw_in_canvas(c)

    t1 = TextRect(3*inch, 1*inch, "My Left Test", _text_dict)
    t1.show_debug_rects = True
    t1.style.set_attr("vert-align", "centre")
    t1.style.set_attr("horz-align", "left")
    t1.rect.move_top_left_to(Point(4.5*inch, 8*inch))
    t1.draw_in_canvas(c)

    t2 = TextRect(3*inch, 1*inch, "My Centre Test", _text_dict)
    t2.show_debug_rects = True
    t2.style.set_attr("vert-align", "centre")
    t2.style.set_attr("horz-align", "centre")
    t2.rect.move_top_left_to(Point(4.5*inch, 6.5*inch))
    t2.draw_in_canvas(c)

    t3 = TextRect(3*inch, 1*inch, "My Right Test", _text_dict)
    t3.show_debug_rects = True
    t3.style.set_attr("vert-align", "centre")
    t3.style.set_attr("horz-align", "right")
    t3.rect.move_top_left_to(Point(4.5*inch, 5*inch))
    t3.draw_in_canvas(c)

    c.showPage()
    c.save()
