# Sample Test passing with nose and pytest

import os
import sys
import pytest
import math
import random

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from toolbox import *
from pdfdoc import *


# def test_safety_init():
#     s = SafetyLabel(
#         icon="caution", title="Danger", desc="Falling Rocks", colour="yellow"
#     )
#     assert s.title.text == "Danger"
#     assert s.desc.text == "Falling Rocks"


# def test_safety_label():
#     c = canvas.Canvas(
#         "./tests/testfiles/test_safetylabel.pdf", pagesize=(8.5 * inch, 11.0 * inch)
#     )
#     c.saveState()
#     s = SafetyLabel(icon="caution", title="Danger", desc="", colour="yellow")
#     s.set_overlayed_symbol("caution", shape="triangle")
#     s.rect = Rect(3.5 * inch, 0.8 * inch)
#     s.compute_cell_sizes("width")
#     s.set_debug_rects(True)
#     s.rect.move_top_left_to(Point(0.5 * inch, 10 * inch))
#     s.draw_in_canvas(c)

#     s.rect.move_top_left_to(Point(0.5 * inch, 9 * inch))
#     s.draw_in_canvas(c, 30)

#     s.set_overlayed_symbol("gloves")
#     s.set_safety_blue()
#     s.rect.move_top_left_to(Point(4.5 * inch, 10 * inch))
#     s.draw_in_canvas(c, 64)

#     s.set_overlayed_symbol("mandatory")
#     s.set_safety_blue()
#     s.rect.move_top_left_to(Point(4.5 * inch, 9 * inch))
#     s.draw_in_canvas(c, 56)

#     s.set_safety_red()
#     s.set_overlayed_symbol("batt-half")
#     s.rect.move_top_left_to(Point(4.5 * inch, 7.5 * inch))
#     s.draw_in_canvas(c)

#     s.set_safety_green()
#     s.set_overlayed_symbol("first-aid")
#     s.rect.move_top_left_to(Point(0.5 * inch, 7.5 * inch))
#     s.draw_in_canvas(c)

#     s.set_overlayed_symbol("info")
#     s.rect.move_top_left_to(Point(0.5 * inch, 8.5 * inch))
#     s.draw_in_canvas(c)

#     s = SafetyLabel(
#         icon="caution", title="Danger", desc="High voltage 240 VAC", colour="yellow"
#     )
#     s.set_overlayed_symbol("electrical", shape="triangle")
#     s.rect = Rect(7 * inch, 2 * inch)
#     s.set_debug_rects(True)
#     s.rect.move_top_left_to(Point(0.5 * inch, 6.5 * inch))
#     s.draw_in_canvas(c, 128)

#     s = SafetyLabel(
#         icon="caution", title="Danger", desc="High voltage", colour="yellow"
#     )
#     s.set_overlayed_symbol("fire", shape="triangle")
#     s.rect = Rect(3.5 * inch, 1.5 * inch)
#     s.set_debug_rects(True)
#     s.rect.move_top_left_to(Point(0.5 * inch, 3 * inch))
#     s.draw_in_canvas(c)

#     s.set_overlayed_symbol("power-off")
#     s.set_safety_blue()
#     s.rect.move_top_left_to(Point(4.5 * inch, 3 * inch))
#     s.draw_in_canvas(c)

#     c.showPage()
#     c.save()


# def test_simple_label():
#     ld = LabelDoc(
#         "./tests/testfiles/test_bigsafety.pdf", style=AVERY_8126_LABEL_DOC_STYLE
#     )
#     labels = [i for i in range(4)]
#     for label in ld.iter_doc(labels):
#         s = SafetyLabel(
#             icon="caution", title="Danger", desc="High voltage", colour="yellow"
#         )
#         s.set_overlayed_symbol("caution", shape="triangle")
#         s.rect = Rect(ld.col_width, ld.row_height)
#         s.set_auto_size(ld.c, 2.5 * inch)
#         s.title.font_size = 72
#         s.show_debug_rects = True
#         ld.add_label(s)


# def test_safety_symbols():
#     from pdfdoc.fonthelpers import haz_lookup_dict, fa_lookup_dict

#     ld = LabelDoc(
#         "./tests/testfiles/test_symbol_list.pdf", style=AVERY_5267_LABEL_DOC_STYLE
#     )
#     labels = [k for k, _ in haz_lookup_dict.items()]
#     labels.extend([k for k, _ in fa_lookup_dict.items()])
#     labels = sorted(labels)
#     for label in ld.iter_doc(labels):
#         sl = TableRow()
#         t1 = TextRect(icon=label, split_lines=False, font_size=22)
#         t2 = TextRect(label, split_lines=False, font_size=13, horz_align="left")
#         sl.add_column(t1, width=0.26)
#         sl.add_column(t2)
#         ld.add_label(sl)


def test_safety_presets():
    c = canvas.Canvas(
        "./tests/testfiles/test_safety_preset.pdf", pagesize=(8.5 * inch, 11.0 * inch)
    )
    s1 = SafetyLabel("icon_info", "Info text 1", width=110 * mm)
    s1.rect.top_left = IN2PTS((1, 10.5))
    s1.draw_in_canvas(c)

    s1 = SafetyLabel(
        "mandatory_icon",
        "Do This Thing",
        size=30,
        aspect_ratio=7,
        description="Failing to do so will result in bad things",
    )
    s1.rect.top_left = IN2PTS((1, 9.25))
    s1.draw_in_canvas(c)

    s1 = SafetyLabel("warning_icon", "Warning", size=24)
    s1.rect.top_left = IN2PTS((1, 7.75))
    s1.draw_in_canvas(c)

    s1 = SafetyLabel(
        "warning_electrical",
        "Danger 240 VAC",
        description="Do not touch exposed live wires inside this box",
        size=40,
        aspect_ratio=6.5,
    )
    s1.rect.top_left = IN2PTS((1, 7))
    s1.draw_in_canvas(c)

    s1 = SafetyLabel("icon_prohibited", "Do not do this", aspect_ratio=6)
    s1.rect.top_left = IN2PTS((1, 4.8))
    s1.draw_in_canvas(c)

    s1 = SafetyLabel("prohibited_touch", "Do not touch this", aspect_ratio=7, size=32)
    s1.rect.top_left = IN2PTS((1, 3.6))
    s1.draw_in_canvas(c)
    s1 = SafetyLabel("prohibited_touch", "Do not touch this", aspect_ratio=6.5, size=32)
    s1.rect.top_left = IN2PTS((1, 2.5))
    s1.draw_in_canvas(c)

    s1 = SafetyLabel("icon_first_aid", "First Aid Kit", size=42)
    s1.rect.top_left = IN2PTS((1, 1.5))
    s1.draw_in_canvas(c)

    c.showPage()
    c.save()


def test_safety_vertical():
    c = canvas.Canvas(
        "./tests/testfiles/test_safety_vertical.pdf", pagesize=(8.5 * inch, 11.0 * inch)
    )
    s1 = SafetyLabel(
        "warning_electrical",
        "Danger",
        description="Do not touch exposed live wires inside this box",
        # description="Do not touch exposed live wires inside this box unless you know what you're doing",
        size=20,
        aspect_ratio=1.2,
        vertical=True,
        force_outlines=False,
    )
    s1.rect.top_left = IN2PTS((1, 10))
    s1.draw_in_canvas(c)

    s1 = SafetyLabel(
        "mandatory_icon",
        "Keep Clear!",
        description="Authorised people only",
        size=20,
        aspect_ratio=1.2,
        vertical=True,
    )
    s1.rect.top_left = IN2PTS((4, 10))
    s1.draw_in_canvas(c)

    s1 = SafetyLabel(
        "mandatory_icon",
        "Fire Door Keep Clear",
        size=30,
        aspect_ratio=1.2,
        vertical=True,
    )
    s1.rect.top_left = IN2PTS((2, 5))
    s1.draw_in_canvas(c)

    c.showPage()
    c.save()
