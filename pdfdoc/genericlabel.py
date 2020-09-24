#! /usr/bin/env python3
#
# Copyright (C) 2020  Fx Bricks Inc.
# This file is part of the legocad python module.
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Generic Label Class

import math

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.colors import Color

from fxgeometry import Rect, Point
from pdfdoc import *

class GenericLabel(TableColumn):
    def __init__(self, title="", subtitle=None, colour=None, pattern=None, symbol=None, image=None, titleimage=None):
        super().__init__(0, 0)
        self.style.set_tb_padding(0.025 * inch)
        self.titlerow = TableRow(0, 0)
        if titleimage is not None:
            self.title = ImageRect(0, 0, filename=titleimage)
        else:
            self.title = TextRect(0, 0, title, GENERIC_LABEL_TITLE)
        if image is not None:
            self.symbol = ImageRect(0, 0, filename=image)
            self.symbol2 = ImageRect(0, 0, filename=image)
        else:
            symbol_text = symbol if symbol is not None else ""
            self.symbol = TextRect(0, 0, symbol_text, GENERIC_SYMBOL_LABEL)
            self.symbol2 = TextRect(0, 0, symbol_text, GENERIC_SYMBOL_LABEL)
        t1, t2 = "", ""
        ht = 0.3
        hp2 = 0.07
        hp = hp2 if pattern is not None else 0
        self.subtitle = TextRect(0, 0, "", GENERIC_LABEL_DESC)
        if subtitle is not None:
            self.subtitle.text = subtitle
        self.pattern = PatternRect(0, 0)
        self.pattern_top = PatternRect(0, 0)
        self.titlerow.add_column("Symbol", self.symbol, width=0.12)
        self.titlerow.add_column("TitleText", self.title, width=AUTO_SIZE)
        self.titlerow.add_column("Symbol2", self.symbol2, width=0.12)
        self.add_row("Title", self.titlerow)
        self.add_row("PatternTop", self.pattern_top)
        self.add_row("Subtitle", self.subtitle)
        self.add_row("Pattern", self.pattern)
        self.set_row_height("PatternTop", hp)
        self.set_row_height("Title", ht)
        self.set_row_height("Subtitle", AUTO_SIZE)
        self.set_row_height("Pattern", hp2)
        if colour is not None:
            self.set_colour(colour)
        else:
            self.set_colour(0)
        if pattern is not None:
            self.set_cell_visible("Pattern", True)
            self.set_cell_visible("PatternTop", True)
            self.pattern.pattern = pattern
            self.pattern_top.pattern = pattern
        else:
            # self.set_cell_visible("Pattern", False)
            self.set_cell_visible("PatternTop", False)
            self.pattern.background_colour = self.pattern.foreground_colour
        if symbol is not None or image is not None:
            self.titlerow.set_cell_visible("Symbol", True)
            self.titlerow.set_cell_visible("Symbol2", True)
        else:
            self.titlerow.set_cell_visible("Symbol", False)
            self.titlerow.set_cell_visible("Symbol2", False)

        self.compute_cell_sizes("height")
        self.pattern.pattern_width = 10
        self.pattern.pattern_slant = 12
        self.pattern_top.pattern_width = 10
        self.pattern_top.pattern_slant = 12
    
    def set_colour(self, colour):
        from ldrawpy import LDRColour
        c = LDRColour(colour)
        self.title.style.set_attr("background-fill", True)
        self.title.style.set_attr("background-colour", c.as_tuple())
        self.title.style.set_attr("border-colour", c.as_tuple())
        self.title.style.set_attr("border-outline", True)
        self.title.style.set_attr(
            "font-colour", c.high_contrast_complement()
        )        
        self.symbol.style.set_attr("background-fill", True)
        self.symbol.style.set_attr("background-colour", c.as_tuple())
        self.symbol.style.set_attr("border-colour", c.as_tuple())
        self.symbol.style.set_attr("border-outline", True)
        self.symbol.style.set_attr(
            "font-colour", c.high_contrast_complement()
        )        
        self.symbol2.style.set_attr("background-fill", True)
        self.symbol2.style.set_attr("background-colour", c.as_tuple())
        self.symbol2.style.set_attr("border-colour", c.as_tuple())
        self.symbol2.style.set_attr("border-outline", True)
        self.symbol2.style.set_attr(
            "font-colour", c.high_contrast_complement()
        )        
        self.pattern.foreground_colour = c.as_tuple()
        self.pattern_top.foreground_colour = c.as_tuple()

    def set_debug_rects(self, show=False):
        self.title.show_debug_rects = show
        self.subtitle.show_debug_rects = show
        self.pattern.show_debug_rects = show
        self.pattern_top.show_debug_rects = show
