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
# Electronic Component Label Class

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
from ldrawpy import LDRColour
from pdfdoc import *

class ElectronicLabel(TableRow):
    def __init__(self, part="", desc="", package=None, colour=None, symbol=None):
        super().__init__(0, 0)
        self.style.set_tb_padding(0.025 * inch)
        filename = symbol if symbol is not None else ""
        self.symbol = ImageRect(0, 0, filename=filename)
        self.symbol.style.set_lr_padding(0.03 * inch)
        self.textcol = TableColumn(0, 0)
        self.titlerow = TableRow(0, 0)
        self.title = TextRect(0, 0, part, GENERIC_LABEL_TITLE)
        self.title.clip_text = True
        self.title.style.set_attr("font-size", 10)
        self.title.style.set_attr("font-name", "DIN-Medium")
        self.title.style.set_attr("horz-align", "left")
        self.title.style.set_attr("right-margin", 0)
        self.title.style.set_attr("right-padding", 0)
        pkgtext = package if package is not None else ""
        self.package = TextRect(0, 0, pkgtext, GENERIC_LABEL_TITLE)
        self.package.clip_text = True
        self.package.style.set_attr("font-size", 8)
        self.package.style.set_attr("font-colour", (0.6, 0.2, 0.2))
        self.package.style.set_attr("font-name", "DIN-Regular")
        self.package.style.set_attr("horz-align", "right")
        self.package.style.set_lr_margins(0)
        self.package.style.set_lr_padding(0)
        self.titlerow.add_column("PartNo", self.title, width=AUTO_SIZE)
        if package is not None:
            self.titlerow.add_column("Package", self.package, width=0.31)
        self.pattern = PatternRect(0, 0)
        self.pattern.pattern = ""
        if colour is not None:
            c = LDRColour(colour)
            self.pattern.style.set_attr("background-fill", True)
            self.pattern.style.set_attr("background-colour", c.as_tuple())
            self.pattern.foreground_colour = c.as_tuple()
            self.pattern.background_colour = c.as_tuple()
        self.subtitle = TextRect(0, 0, "", GENERIC_LABEL_DESC)
        self.subtitle.style.set_attr("font-size", 8)
        self.subtitle.style.set_attr("font-name", "DIN-Regular")
        self.subtitle.style.set_attr("horz-align", "left")
        if desc is not None:
            self.subtitle.text = desc
        self.textcol.add_row("Title", self.titlerow, height=AUTO_SIZE)
        self.textcol.add_row("Pattern", self.pattern, height=0.07)
        self.textcol.add_row("Desc", self.subtitle, height=AUTO_SIZE)
        if symbol is not None:
            self.add_column("Symbol", self.symbol, width=0.22)
        self.add_column("Text", self.textcol, width=AUTO_SIZE)
        self.compute_cell_sizes("width")
    

    def set_debug_rects(self, show=False):
        self.title.show_debug_rects = show
        self.package.show_debug_rects = show
        self.subtitle.show_debug_rects = show
        self.pattern.show_debug_rects = show
        self.symbol.show_debug_rects = show
