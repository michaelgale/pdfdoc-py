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


class GenericLabel(TableColumn):
    def __init__(
        self,
        title="",
        subtitle=None,
        colour=None,
        pattern=None,
        symbol=None,
        image=None,
        titleimage=None,
        bottom_pattern=True,
    ):
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
            if symbol_text.lower().endswith(".svg"):
                self.symbol = SvgRect.from_preset(symbol_text)
                self.symbol2 = SvgRect.from_preset(symbol_text)
            elif symbol_text.lower().endswith(".png"):
                self.symbol = ImageRect.from_preset(symbol_text)
                self.symbol2 = ImageRect.from_preset(symbol_text)
            else:
                self.symbol = TextRect(0, 0, symbol_text, GENERIC_SYMBOL_LABEL)
                self.symbol2 = TextRect(0, 0, symbol_text, GENERIC_SYMBOL_LABEL)
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
        if bottom_pattern:
            self.add_row("Pattern", self.pattern)
        self.set_row_height("PatternTop", hp)
        self.set_row_height("Title", ht)
        self.set_row_height("Subtitle", AUTO_SIZE)
        if bottom_pattern:
            self.set_row_height("Pattern", hp2)
        if colour is not None:
            self.set_colour(colour)
        else:
            self.set_colour(0)
        if pattern is not None:
            if bottom_pattern:
                self.set_cell_visible("Pattern", True)
                self.pattern.pattern = pattern
            self.set_cell_visible("PatternTop", True)
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
        c = safe_colour_tuple(colour)
        self.title.background_colour = c
        self.title.border_colour = c
        self.title.border_outline = True
        self.title.font_colour = high_contrast_complement(c)
        self.symbol.background_colour = c
        self.symbol.border_colour = c
        self.symbol.border_outline = True
        self.symbol.font_colour = high_contrast_complement(c)
        self.symbol2.background_colour = c
        self.symbol2.border_colour = c
        self.symbol2.border_outline = True
        self.symbol2.font_colour = high_contrast_complement(c)
        self.pattern.foreground_colour = c
        self.pattern_top.foreground_colour = c

    def set_debug_rects(self, show=False):
        self.title.show_debug_rects = show
        self.subtitle.show_debug_rects = show
        self.pattern.show_debug_rects = show
        self.pattern_top.show_debug_rects = show
