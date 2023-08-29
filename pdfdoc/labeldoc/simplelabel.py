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
        self.title.font_size = 10
        self.title.font_name = "IKEA-Sans-Heavy"
        self.title.horz_align = "left"
        self.title.right_margin = 0
        self.title.right_padding = 0

        self.line2 = TextRect(0, 0, line2, GENERIC_LABEL_TITLE)
        self.line2.text = line2
        self.line2.clip_text = True
        self.line2.font_size = 7
        self.line2.font_name = "DroidSans"
        self.line2.horz_align = "left"
        self.line2.right_margin = 0
        self.line2.right_padding = 0

        self.line3 = TextRect(0, 0, line3, GENERIC_LABEL_TITLE)
        self.line3.text = line3
        self.line3.clip_text = True
        self.line3.font_size = 7
        self.line3.font_name = "DroidSans"
        self.line3.horz_align = "left"
        self.line3.right_margin = 0
        self.line3.right_padding = 0

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
        self.textlabel.font_size = 11
        self.textlabel.font_name = "DIN-Medium"
        self.textlabel.horz_align = "left"
        self.textlabel.right_margin = 0
        self.textlabel.right_padding = 0
        self.textlabel.line_spacing = 1.2
        self.style.set_lr_padding(0.025 * inch)
        self.add_column("Label", self.textlabel, width=AUTO_SIZE)
        self.compute_cell_sizes("width")

    def set_debug_rects(self, show=False):
        self.title.show_debug_rects = show
        self.line2.show_debug_rects = show
        self.line3.show_debug_rects = show
