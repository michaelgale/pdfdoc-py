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
# Generic ContentRect parent container class

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
from .pdfdoc import *
from .docstyle import DocStyle


class ContentRect:
    def __init__(self, w=1, h=1, style=None):
        self.rect = Rect()
        self.rect.set_size(w, h)
        self.style = DocStyle()
        if style is not None:
            self.style.set_with_dict(style)
        self.show_debug_rects = False
        self.overlay_content = None

    def __str__():
        return "Content Rect: %s" % (self.rect)

    def draw_debug_rect(self, c, r, colour=(0, 0, 0)):
        c.setFillColor(rl_colour_trans())
        c.setStrokeColor(rl_colour(colour))
        c.setLineWidth(0.1)
        c.rect(r.left, r.bottom, r.width, r.height, stroke=True, fill=False)

    def draw_in_canvas(self, c):
        self.draw_rect(c)
        if self.show_debug_rects:
            self.draw_debug_rect(c, self.rect)
            inset_rect = self.style.get_inset_rect(self.rect)
            self.draw_debug_rect(c, inset_rect, (0, 0, 1))

    def draw_rect(self, c):
        has_background = self.style.get_attr("background-fill", False)
        background_colour = self.style.get_attr("background-colour", (1, 1, 1))
        if has_background:
            fc = rl_colour(background_colour)
            c.setFillColor(fc)
        else:
            fc = rl_colour_trans()
        has_border = self.style.get_attr("border-outline", False)
        if has_border:
            border_colour = self.style.get_attr("border-colour", (1, 1, 1))
            border_width = self.style.get_attr("border-width", 0)
            rc = rl_colour(border_colour)
            c.setStrokeColor(rc)
            c.setLineWidth(border_width)
        mrect = self.style.get_margin_rect(self.rect)
        border_radius = self.style.get_attr("border-radius", 0)
        if border_radius > 0:
            c.roundRect(
                mrect.left,
                mrect.bottom,
                mrect.width,
                mrect.height,
                radius=border_radius,
                stroke=has_border,
                fill=has_background,
            )
        else:
            c.rect(
                mrect.left,
                mrect.bottom,
                mrect.width,
                mrect.height,
                stroke=has_border,
                fill=has_background,
            )
