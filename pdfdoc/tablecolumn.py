#! /usr/bin/env python3
#
# Copyright (C) 2018  Fx Bricks Inc.
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
# TableColumn class derived from TableVector

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
from .docstyle import DocStyle
from .pdfdoc import rl_colour, rl_colour_trans
from .tablecell import TableCell, TableVector


class TableColumn(TableVector):
    def __init__(self, w, h, style=None):
        super().__init__(w, h, style)

    def add_row(self, label, content, order=None, height=0):
        if order is not None:
            cell = TableCell(label, content, order, 0, height)
        else:
            cell = TableCell(label, content, len(self.cells), 0, height)
        self.cells.append(cell)

    def set_row_order(self, label, order):
        self.set_cell_order(label, order)

    def set_row_height(self, label, height):
        cell = self.get_cell(label)
        if cell is not None:
            cell.height = height

    def draw_in_canvas(self, canvas, auto_size=False, auto_size_anchor=None):
        if auto_size:
            w, h = self.get_content_size()
            anchor = "top left" if auto_size_anchor is None else auto_size_anchor
            self.rect.set_size_anchored(w, h, anchor_pt=anchor)
        self.draw_cells_in_canvas(canvas, "height")

    def set_cell_content(self, label, content):
        cell = self.get_cell(label)
        if cell is not None:
            cell.content = content
            self.compute_cell_sizes("height")

    def get_content_size(self, with_padding=True):
        sw, sh = 0, 0
        for cell in self.iter_cells():
            cw, ch = cell.content.get_content_size()
            if cw > 0:
                sw = max(sw, cw)
            sh += ch
        if with_padding:
            sw += self.style.get_width_trim()
            sh += self.style.get_height_trim()
        self.total_width = sw
        self.total_height = sh
        return sw, sh
