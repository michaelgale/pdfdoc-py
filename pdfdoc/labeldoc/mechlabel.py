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
# Generic Label Class

import math

from reportlab.pdfgen import canvas

from toolbox import *
from pdfdoc import *


class MechanicalLabel(TableRow):
    def __init__(self, title="", subtitle=None, colour=None, symbol=None):
        from ldrawpy import LDRColour

        super().__init__(0, 0)
        self.style.set_tb_padding(0.025 * inch)
        filename = symbol if symbol is not None else ""
        self.symbol = ImageRect(0, 0, filename=filename)
        self.symbol.style.set_lr_padding(0.03 * inch)
        self.textcol = TableColumn(0, 0)
        self.titlerow = TableRow(0, 0)
        self.title = TextRect(0, 0, title, GENERIC_LABEL_TITLE)
        self.title.style.set_attr("font-size", 12)
        self.title.style.set_attr("font-name", "IKEA-Sans-Heavy")
        self.title.style.set_attr("horz-align", "left")
        self.auxtitle = TextRect(0, 0, title, GENERIC_LABEL_TITLE)
        self.auxtitle.style.set_attr("font-size", 12)
        self.auxtitle.style.set_attr("font-name", "IKEA-Sans-Heavy")
        self.auxtitle.style.set_attr("horz-align", "left")
        if title[0] == "#" or title[0] == "`":
            titletext = title.split()[0]
            auxtext = title.split()[1:]
            auxtext = " ".join(auxtext)
            if title[0] == "`":
                self.title.text = titletext[1:]
            else:
                self.title.text = titletext
            self.auxtitle.text = auxtext
            if len(titletext) < 4:
                self.titlerow.add_column("Type", self.title, width=0.28)
            elif len(titletext) >= 8:
                self.titlerow.add_column("Type", self.title, width=0.6)
            elif len(titletext) > 5:
                self.titlerow.add_column("Type", self.title, width=0.48)
            else:
                self.titlerow.add_column("Type", self.title, width=0.42)

            self.titlerow.add_column("Aux", self.auxtitle, width=AUTO_SIZE)
            c = LDRColour(colour)
            self.title.style.set_attr("background-colour", c.as_tuple())
            self.title.style.set_attr("background-fill", True)
            self.title.style.set_attr("horz-align", "centre")
            self.title.style.set_attr("font-colour", c.high_contrast_complement())
        else:
            self.titlerow.add_column("Type", self.title, width=AUTO_SIZE)
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
        if subtitle is not None:
            self.subtitle.text = subtitle
        self.textcol.add_row("Title", self.titlerow, height=AUTO_SIZE)
        self.textcol.add_row("Pattern", self.pattern, height=0.07)
        self.textcol.add_row("SubTitle", self.subtitle, height=AUTO_SIZE)
        if symbol is not None:
            self.add_column("Symbol", self.symbol, width=0.22)
        self.add_column("Text", self.textcol, width=AUTO_SIZE)
        self.compute_cell_sizes("width")

    def set_debug_rects(self, show=False):
        self.title.show_debug_rects = show
        self.subtitle.show_debug_rects = show
        self.pattern.show_debug_rects = show
        self.symbol.show_debug_rects = show
