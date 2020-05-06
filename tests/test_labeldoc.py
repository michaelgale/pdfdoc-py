# Sample Test passing with nose and pytest

import os
import sys
import pytest
import math
import random

from reportlab.lib.units import inch
from fxgeometry import Point
from ldrawpy import LDRColour
from pdfdoc import *

_test_dict = {"left-margin": 1 * inch, "right-margin": 1 * inch, "horz-align": "left"}

def test_labeldoc_init():
    ld = LabelDoc("test_labeldoc.pdf", style=AVERY_5164_LABEL_DOC_STYLE)
    assert ld.nrows == 3
    assert ld.ncolumns == 2
    assert ld.total_rows == 3
    assert ld.total_columns == 3

def test_content_idx():
    ld = LabelDoc("test_labeldoc.pdf", style=AVERY_5164_LABEL_DOC_STYLE)
    rx = [0, 0, 1, 1, 2, 2, 0, 0, 1, 1]
    cx = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    for i, x in enumerate(range(10)):
        r, c = ld.get_row_col(x)
        assert r == rx[i] and c == cx[i]

def test_labeldoc_iter():
    ld = LabelDoc("test_labeldoc.pdf", style=AVERY_5262_LABEL_DOC_STYLE)
    labels = [i for i in range(25)]
    for label, row, col in ld.iter_label(labels):
        tr = TextRect(withText="Label %d" % (label))
        tr.show_debug_rects = True
        ld.set_table_cell(tr, row, col)

def test_generic_labeldoc():
    ld = LabelDoc("test_generic_label.pdf", style=AVERY_5263_LABEL_DOC_STYLE)
    labels = [i for i in range(25)]
    for label, row, col in ld.iter_label(labels):
        rt = random.random()
        if rt > 0.67:
            subtitle = "This is a really long bit of text for the subtitle which is more than one line"
        elif rt < 0.33:
            subtitle = "Subtitle Line"
        else:
            subtitle = None
        rp = random.random()
        if rp > 0.85:
            show_pattern = "slant-line"
        elif rp < 0.15:
            show_pattern = "squares"
        else:
            show_pattern = None
        if random.random() > 0.5:
            colour = random.randint(0, 100)
        else:
            colour = None
        gl = GenericLabel(title="Label %d" % (label), subtitle=subtitle, colour=colour, pattern=show_pattern)
        gl.set_debug_rects(True)
        ld.set_table_cell(gl, row, col)
