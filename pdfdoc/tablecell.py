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
# Table cell class

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


class TableCell:
    def __init__(self, label, content=None, order=0, width=0, height=0):
        self.label = label
        self.content = content
        self.order = order
        self.width = width
        self.height = height

class TableVector:
    def __init__(self, w, h, style=None):
        self.rect = Rect()
        self.rect.set_size(w, h)
        self.clip_text = False
        self.style = DocStyle()
        if style is not None:
            self.style.set_with_dict(style)
        self.cells = []
        self.cell_order = []

    def __len__(self):
        return len(self.cells)

    def set_cell_order(self, label, order):
        for cell in self.cells:
            if cell.label == label:
                cell.order = order

    def compute_cell_order(self):
        order = []
        labels = []
        for cell in self.cells:
            order.append(cell.order)
            labels.append(cell.label)
        cells = zip(order, labels)
        ocells = sorted(cells, key=lambda x: x[0])
        self.cell_order = []
        for cell in ocells:
            self.cell_order.append(cell[1])

    def compute_cell_sizes(self, axis="width"):
        self.compute_cell_order()
        cell_rect = self.style.get_inset_rect(self.rect)
        if axis == "width":
            total_limit = cell_rect.width
        else:
            total_limit = cell_rect.height
        acc_size = 0
        unassigned = []

        # set cell size for cells with a specification
        for cell_label in self.cell_order:
            for cell in self.cells:
                if cell_label == cell.label:
                    if axis == "width":
                        if cell.width > 0:
                            cwidth = cell.width * total_limit
                            cell.content.rect.set_size(cwidth, cell_rect.height)
                            acc_size += cwidth
                        else:
                            unassigned.append(cell_label)
                    else:
                        if cell.height > 0:
                            cheight = cell.height * total_limit
                            cell.content.rect.set_size(cell_rect.width, cheight)
                            acc_size += cheight
                        else:
                            unassigned.append(cell_label)

        # set cell sizes for remaining cells automatically
        # based on the remaining space in the table vector
        rem_size = total_limit - acc_size
        for ucell in unassigned:
            if rem_size > 0:
                csize = rem_size / len(unassigned)
            else:
                csize = 0
            for cell in self.cells:
                if cell.label == ucell:
                    if axis == "width":
                        cell.content.rect.set_size(csize, cell_rect.height)
                    else:
                        cell.content.rect.set_size(cell_rect.width, csize)
                    acc_size += csize

        # move each cells's origin based on the cell order
        cx = cell_rect.left
        cy = cell_rect.top
        for cell_label in self.cell_order:
            for cell in self.cells:
                if cell_label == cell.label:
                    cell.content.rect.move_top_left_to(Point(cx, cy))
                    if axis == "width":
                        cx += cell.content.rect.width
                    else:
                        cy -= cell.content.rect.height

    def draw_border_lines(self, c):
        border_colour = self.style.get_attr("border-colour", (1, 1, 1))
        border_width = self.style.get_attr("border-width", 0)
        c.setStrokeColor(rl_colour(border_colour))
        c.setLineWidth(border_width)
        mrect = self.style.get_margin_rect(self.rect)
        if self.style.get_attr("border-line-left", False):
            c.line(mrect.left, mrect.top, mrect.left, mrect.bottom)
        if self.style.get_attr("border-line-right", False):
            c.line(mrect.right, mrect.top, mrect.right, mrect.bottom)
        if self.style.get_attr("border-line-top", False):
            c.line(mrect.left, mrect.top, mrect.right, mrect.top)
        if self.style.get_attr("border-line-bottom", False):
            c.line(mrect.left, mrect.bottom, mrect.right, mrect.bottom)

    def draw_cells_in_canvas(self, canvas, axis):
        self.compute_cell_sizes(axis)
        for cell in self.cells:
            cell.content.draw_in_canvas(canvas)
        self.draw_border_lines(canvas)
