# Sample Test passing with nose and pytest

import os
import sys
import pytest

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from toolbox import *
from pdfdoc import *


_test_dict = {"left-margin": 2, "right-margin": 3, "horz-align": "left"}


def test_imgrect_init():
    t1 = ImageRect(10, 2, "./testfiles/test.png")
    assert t1.rect.left == -5
    assert t1.rect.right == 5
    assert t1.rect.top == 1
    assert t1.rect.bottom == -1


def test_imgrect_pos():
    t1 = ImageRect(10, 2, "./testfiles/test.png", _test_dict)
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
    "top-margin": 0.25 * inch,
    "bottom-margin": 0.025 * inch,
    "left-margin": 0.15 * inch,
    "right-margin": 0.05 * inch,
    "top-padding": 0.1 * inch,
    "bottom-padding": 0.2 * inch,
    "left-padding": 0.15 * inch,
    "right-padding": 0.25 * inch,
}


def test_imgrect_render():
    c = canvas.Canvas(
        "./testfiles/test_imgrect.pdf", pagesize=(8.5 * inch, 11.0 * inch)
    )
    c.saveState()
    t1 = ImageRect(1 * inch, 2 * inch, "./testfiles/long.png", _text_dict)
    t1.show_debug_rects = True
    t1.vert_align = "top"
    t1.top_left = 1 * inch, 8 * inch
    t1.draw_in_canvas(c)

    t2 = ImageRect(1 * inch, 2 * inch, "./testfiles/tall.png", _text_dict)
    t2.show_debug_rects = True
    t2.vert_align = "centre"
    t2.top_left = 1 * inch, 5.5 * inch
    t2.draw_in_canvas(c)

    t3 = ImageRect(1 * inch, 2 * inch, "./testfiles/square.png", _text_dict)
    t3.show_debug_rects = True
    t3.vert_align = "bottom"
    t3.top_left = 1 * inch, 3 * inch
    t3.draw_in_canvas(c)

    t1 = ImageRect(3 * inch, 1 * inch, "./testfiles/long.png", _text_dict)
    t1.show_debug_rects = True
    t1.horz_align = "left"
    t1.top_left = 4.5 * inch, 8 * inch
    t1.draw_in_canvas(c)

    t2 = ImageRect(3 * inch, 1 * inch, "./testfiles/tall.png", _text_dict)
    t2.show_debug_rects = True
    t2.horz_align = "centre"
    t2.top_left = 4.5 * inch, 6.5 * inch
    t2.draw_in_canvas(c)

    t3 = ImageRect(3 * inch, 1 * inch, "./testfiles/square.png", _text_dict)
    t3.show_debug_rects = True
    t3.horz_align = "right"
    t3.top_left = 4.5 * inch, 5 * inch
    t3.draw_in_canvas(c)

    c.showPage()
    c.save()


def test_transparent_intersect():
    fn = "./testfiles/long.png"
    r1 = Rect(10, 10)
    r1.move_top_left_to((0, 10))
    x = is_rect_in_transparent_region(fn, r1)
    assert x
    r1.move_top_left_to((230, 125))
    x = is_rect_in_transparent_region(fn, r1)
    assert not x
    r1.move_top_left_to((430, 230))
    x = is_rect_in_transparent_region(fn, r1)
    assert x


def test_list_presets():
    ld = LabelDoc(
        "./testfiles/test_img_preset_list.pdf", style=AVERY_5260_LABEL_DOC_STYLE
    )

    presets = ImageRect.list_presets()
    for _, file in enumerate(ld.iter_doc(presets)):
        tr = TableRow()
        tr.add_column("img", ImageRect(filename=file))
        _, fn = split_path(file)
        tr.add_column(
            "label", TextRect(str(fn), horz_align="left", font_size=10, left_padding=8)
        )
        tr.set_column_width("img", 0.3)
        ld.add_label(tr)
