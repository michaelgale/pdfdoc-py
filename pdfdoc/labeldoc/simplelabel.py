#! /usr/bin/env python3
#
# Copyright (C) 2020  Michael Gale

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
# Simple Label Class


import math

from reportlab.pdfgen import canvas

from toolbox import *
from pdfdoc import *


class SimpleLabel(TableRow):
    def __init__(self, line1="", line2="", line3=""):
        super().__init__(0, 0)
        self.style.set_tb_padding(0.025 * inch)
        self.textcol = TableColumn(0, 0)
        self.title = TextRect(0, 0, line1, GENERIC_LABEL_TITLE)
        self.title.text = line1
        self.title.clip_text = True
        self.title.style.set_attr("font-size", 10)
        self.title.style.set_attr("font-name", "IKEA-Sans-Heavy")
        self.title.style.set_attr("horz-align", "left")
        self.title.style.set_attr("right-margin", 0)
        self.title.style.set_attr("right-padding", 0)

        self.line2 = TextRect(0, 0, line2, GENERIC_LABEL_TITLE)
        self.line2.text = line2
        self.line2.clip_text = True
        self.line2.style.set_attr("font-size", 7)
        self.line2.style.set_attr("font-name", "DroidSans")
        self.line2.style.set_attr("horz-align", "left")
        self.line2.style.set_attr("right-margin", 0)
        self.line2.style.set_attr("right-padding", 0)

        self.line3 = TextRect(0, 0, line3, GENERIC_LABEL_TITLE)
        self.line3.text = line3
        self.line3.clip_text = True
        self.line3.style.set_attr("font-size", 7)
        self.line3.style.set_attr("font-name", "DroidSans")
        self.line3.style.set_attr("horz-align", "left")
        self.line3.style.set_attr("right-margin", 0)
        self.line3.style.set_attr("right-padding", 0)

        self.textcol.add_row("Title", self.title, height=0.37)
        self.textcol.add_row("Line2", self.line2, height=AUTO_SIZE)
        self.textcol.add_row("Line3", self.line3, height=AUTO_SIZE)
        self.add_column("Label", self.textcol, width=AUTO_SIZE)
        self.compute_cell_sizes("width")

    def set_debug_rects(self, show=False):
        self.title.show_debug_rects = show
        self.line2.show_debug_rects = show
        self.line3.show_debug_rects = show


class PlainTextLabel(TableRow):
    def __init__(self, text=""):
        super().__init__(0, 0)
        self.style.set_tb_padding(0.025 * inch)
        self.textlabel = TextRect(0, 0, text, GENERIC_LABEL_TITLE)
        self.textlabel.text = text
        self.textlabel.style.set_attr("font-size", 11)
        self.textlabel.style.set_attr("font-name", "DIN-Medium")
        self.textlabel.style.set_attr("horz-align", "left")
        self.textlabel.style.set_attr("right-margin", 0)
        self.textlabel.style.set_attr("right-padding", 0)
        self.textlabel.style["line-spacing"] = 1.2
        self.style.set_lr_padding(0.025 * inch)
        self.add_column("Label", self.textlabel, width=AUTO_SIZE)
        self.compute_cell_sizes("width")

    def set_debug_rects(self, show=False):
        self.title.show_debug_rects = show
        self.line2.show_debug_rects = show
        self.line3.show_debug_rects = show
