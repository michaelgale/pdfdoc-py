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
# Table row class

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

def keyOrder(elem):
    return elem.order

class Column:
    def __init__(self, label, content=None, order=0, width=0):
        self.label = label
        self.content = content
        self.order = order
        self.width = width

class TableRow:
    def __init__(self, w, h, style=None):
        self.rect = Rect()
        self.rect.set_size(w, h)
        self.clip_text = False
        self.style = DocStyle()
        if style is not None:
            self.style.set_with_dict(style)
        self.columns = []
        self.column_order = []

    def __len__(self):
        return len(self.columns)

    def add_column(self, label, content, order=None, width=0):
        if order is not None:
            column = Column(label, content, order, width)
        else:
            column = Column(label, content, len(self.columns), width)
        self.columns.append(column)

    def set_column_order(self, label, order):
        for column in self.columns:
            if column.label == label:
                column.order = order

    def set_column_width(self, label, width):
        for column in self.columns:
            if column.label == label:
                column.width = width

    def compute_column_widths(self):
        self.compute_column_order()
        row_rect = self.style.get_inset_rect(self.rect)
        total_width = row_rect.width
        acc_width = 0
        unassigned = []

        # set column widths for columns with a specification
        for col_label in self.column_order:
            for column in self.columns:
                if col_label == column.label:
                    if column.width > 0:
                        cwidth = column.width * total_width
                        column.content.rect.set_size(cwidth, row_rect.height)
                        acc_width += cwidth
                    else:
                        unassigned.append(col_label)

        # set column widths for remaining columns automatically
        # based on the remaining space in the row
        rem_width = total_width - acc_width
        for col in unassigned:
            if rem_width > 0:
                cwidth = rem_width / len(unassigned)
            else:
                cwidth = 0
            for column in self.columns:
                if column.label == col:
                    column.content.rect.set_size(cwidth, row_rect.height)
                    acc_width += cwidth

        # move each column's origin based on the column order and width
        cx = row_rect.left
        cy = row_rect.top
        for col_label in self.column_order:
            for column in self.columns:
                if col_label == column.label:
                    column.content.rect.move_top_left_to(Point(cx, cy))
                    cx += column.content.rect.width

    def draw_in_canvas(self, canvas):
        row_rect = self.style.get_inset_rect(self.rect)
        self.compute_column_widths()
        for column in self.columns:
            column.content.draw_in_canvas(canvas)

    def compute_column_order(self):
        order = []
        labels = []
        for column in self.columns:
            order.append(column.order)
            labels.append(column.label)
        cols = zip(order, labels)
        ocols = sorted(cols, key=lambda x: x[0])
        self.column_order = []
        for col in ocols:
            self.column_order.append(col[1])
