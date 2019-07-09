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

from fxgeometry import Rect
from docstyle import *
from pdfdoc import rl_colour, rl_colour_trans

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

    def compute_column_widths(self):
        self.columns.sort(key=keyOrder)
        row_rect = self.style.get_inset_rect(self.rect)
        total_width = row_rect.width
        acc_width = 0
        unassigned = []
        for i, column in enumerate(self.columns):
            if column.width > 0:
                cwidth = column.width * total_width
                column.content.rect.set_size(cwidth, row_rect.height)
                (cx, cy) = (row_rect.left + acc_width, row_rect.top)
                column.content.rect.move_top_left_to((cx, cy))
                acc_width += cwidth
            else:
                unassigned.append(i)
        rem_width = total_width - acc_width
        for col in unassigned:
            if rem_width > 0:
                cwidth = rem_width / len(unassigned)
            else:
                cwidth = 0
            self.columns[col].content.rect.set_size(cwidth, row_rect.height)
            (cx, cy) = (row_rect.left + acc_width, row_rect.top)
            self.columns[col].content.rect.move_top_left_to((cx, cy))
            acc_width += cwidth

    def draw_in_canvas():
        row_rect = self.style.get_inset_rect(self.rect)
        self.compute_column_widths()
        for column in self.columns:
            column.content.draw_in_canvas()
