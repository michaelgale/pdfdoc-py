# Sample Test passing with nose and pytest

import os
import sys
import pytest

from toolbox import *
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import inch
from pdfdoc import *
from rich import inspect

_test_dict = {"left-margin": 2, "right-margin": 3, "horz-align": "left"}


# def test_line_metrics():
#     c = canvas.Canvas("./tests/testfiles/test_line_metrics.pdf")
#     c.saveState()
#     tx = 1 * inch
#     ty = 10 * inch
#     for font_name in ["IKEA-Sans-Heavy", "DroidSans", "DIN-Medium", "GDSTransport"]:
#         font_size = 24
#         c.setFont(font_name, font_size)
#         text = "A font goes up and down"
#         tw, th = get_string_metrics(c, text, font_name, font_size)
#         face = pdfmetrics.getFont(font_name).face
#         ascent, descent = (face.ascent / 1000.0), face.descent / 1000.0
#         hh = (face.ascent - face.descent) / 1000.0 * font_size
#         ta, td = ascent * font_size, descent * font_size
#         # ta, td = get_string_asc_des(c, text, font_name, font_size)
#         _, thd = get_string_metrics(
#             c, text, font_name, font_size, with_descent=False
#         )
#         if abs(ta - font_size) < 2:
#             hh = ta
#         else:
#             hh = ta - td
#         print("The text: '%s' in font: %s-%d" % (text, font_name, font_size))
#         print("  width: %.2f  height: %.2f" % (tw, th))
#         print("  ascender: %.2f  descent: %.2f" % (ta, td))
#         print("Line height can be:")
#         print("  th + ta : %.2f" % (th + ta))
#         print("  thd     : %.2f" % (thd))
#         c.setFillColor((0.9, 0.5, 0.5))
#         c.rect(tx, ty + td, tw, hh, stroke=0, fill=1)
#         c.setStrokeColor((0, 0, 1))
#         c.rect(tx, ty, tw, thd, stroke=1, fill=0)
#         c.setStrokeColor((0, 0.5, 0))
#         c.rect(tx, ty, tw, ta, stroke=1, fill=0)
#         c.setFillColor((0, 0, 0))
#         c.drawString(tx, ty, text)
#         c.drawString(tx, ty - 1 * inch, "h:%.2f hh:%.2f a:%.2f d:%.2f" % (th, hh, ta, td))
#         ty -= 2 * inch
#     c.showPage()
#     c.save()

# def test_font_wrapper():
#     for font_name in ["IKEA-Sans-Heavy", "DroidSans", "DIN-Medium", "GDSTransport"]:
#         font_size = 24
#         fw = FontWrapper(font_name, font_size)
#         print(font_name, font_size)
#         print("  asc:", fw.ascent, "desc:", fw.descent, "sw:", fw.stroke_width)
#         print("  nom:", fw.nom_height, "height:", fw.height)


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
        "./tests/testfiles/test_splitlines.pdf", pagesize=(8.5 * inch, 11.0 * inch)
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


def test_string_splitting():
    c = canvas.Canvas(
        "./tests/testfiles/test_kerning.pdf", pagesize=(8.5 * inch, 11.0 * inch)
    )
    t1 = TextRect(4 * inch, 1.5 * inch, "No Kerning", _text_dict)
    t1.background_fill = True
    t1.background_colour = "#90E090"
    t1.show_debug_rects = True
    t1.top_left = 0.5 * inch, 9 * inch
    t1.draw_in_canvas(c)

    t1 = TextRect(4 * inch, 1.5 * inch, "Pos Kerning", _text_dict)
    t1.kerning = 0.5
    t1.top_left = 0.5 * inch, 6 * inch
    t1.show_debug_rects = True
    t1.draw_in_canvas(c)

    t1 = TextRect(4 * inch, 1.5 * inch, "Neg Kerning", _text_dict)
    t1.kerning = -0.1
    t1.top_left = 0.5 * inch, 3 * inch
    t1.show_debug_rects = True
    t1.draw_in_canvas(c)

    t1 = TextRect(4 * inch, 1.5 * inch, "Rotated", _text_dict)
    t1.rotation = 45
    t1.background_fill = True
    t1.background_colour = "#F0E090"
    t1.background_alpha = 0.5
    t1.border_alpha = 0.3
    t1.font_alpha = 0.5
    t1.show_debug_rects = True
    t1.top_left = 4 * inch, 8.25 * inch
    t1.draw_in_canvas(c)

    c.showPage()
    c.save()


def test_textrect_render():
    c = canvas.Canvas(
        "./tests/testfiles/test_textrect.pdf", pagesize=(8.5 * inch, 11.0 * inch)
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
