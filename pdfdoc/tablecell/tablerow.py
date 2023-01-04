#! /usr/bin/env python3
#
# Copyright (C) 2020  Michael Gale
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
# TableRow class derived from TableVector

from toolbox import *
from pdfdoc import *


class TableRow(TableVector):
    def __init__(self, w=0, h=0, style=None):
        super().__init__(w, h, style)

    def add_column(self, label, content, order=None, width=0):
        if order is not None:
            column = TableCell(label, content, order, width)
        else:
            column = TableCell(label, content, len(self.cells), width)
        self.cells.append(column)

    def set_column_order(self, label, order):
        self.set_cell_order(label, order)

    def set_column_width(self, label, width):
        cell = self[label]
        if cell is not None:
            cell.width = width

    def draw_in_canvas(self, canvas, auto_size=False, auto_size_anchor=None):
        if auto_size:
            w, h = self.get_content_size()
            anchor = "top left" if auto_size_anchor is None else auto_size_anchor
            self.rect.set_size_anchored(w, h, anchor_pt=anchor)
        self.draw_cells_in_canvas(canvas, "width")

    def set_cell_content(self, label, content):
        cell = self[label]
        if cell is not None:
            cell.content = content
            self.compute_cell_sizes("width")

    def get_content_size(self, with_padding=True):
        sw, sh = 0, 0
        for cell in self.iter_cells():
            cw, ch = cell.content.get_content_size()
            if ch > 0:
                sh = max(sh, ch)
            sw += cw
        if with_padding:
            sw += self.style.get_width_trim()
            sh += self.style.get_height_trim()
        self.total_width = self.fixed_rect.width if self.is_fixed_width else sw
        self.total_height = self.fixed_rect.height if self.is_fixed_height else sh
        if self.min_width:
            self.total_width = max(self.total_width, self.min_width)
        if self.min_height:
            self.total_height = max(self.total_height, self.min_height)
        return self.total_width, self.total_height
