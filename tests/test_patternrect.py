# Sample Test passing with nose and pytest

import os
import sys
import pytest

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from toolbox import *
from pdfdoc import *


def test_patternrect_render():
    c = canvas.Canvas(
        "./tests/testfiles/test_patternrect.pdf", pagesize=(8.5 * inch, 11.0 * inch)
    )
    c.saveState()
    t1 = PatternRect(6 * inch, 0.75 * inch)
    t1.pattern_slant = 9
    t1.show_debug_rects = True
    t1.rect.move_top_left_to(Point(1 * inch, 8 * inch))
    t1.draw_in_canvas(c)

    t1 = PatternRect(0.75 * inch, 6 * inch)
    t1.pattern_slant = 9
    t1.show_debug_rects = True
    t1.rect.move_top_left_to(Point(1 * inch, 8 * inch))
    t1.draw_in_canvas(c)

    t2 = PatternRect(5 * inch, 0.5 * inch)
    t2.show_debug_rects = True
    t2.pattern = "squares"

    t2.pattern_width = 8
    t2.rect.move_top_left_to(Point(2 * inch, 3 * inch))
    t2.draw_in_canvas(c)

    c.showPage()
    c.save()
