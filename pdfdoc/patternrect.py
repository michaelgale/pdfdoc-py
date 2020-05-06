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
# Pattern filled ContentRect derived class

import math

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
from pdfdoc import *


class PatternRect(ContentRect):
    def __init__(self, w=1, h=1, pattern=None, style=None):
        super().__init__(w, h, style)
        if pattern is not None:
            self.pattern = pattern
        else:
            self.pattern = "slant-line"
        self.pattern_width = 18.0
        self.pattern_slant = 18.0
        self.background_colour = (1, 1, 1)
        self.foreground_colour = (1, 0, 0)

    def draw_in_canvas(self, c):
        self.draw_rect(c)
        self.draw_pattern_rect(c)
        if self.show_debug_rects:
            self.draw_debug_rect(c, self.rect)
            inset_rect = self.style.get_inset_rect(self.rect)
            self.draw_debug_rect(c, inset_rect, (0, 0, 1))

    def _draw_slant_line(self, c, fc):
        mrect = self.style.get_margin_rect(self.rect)
        x0, x1 = mrect.left, mrect.right
        y0, y1 = mrect.bottom, mrect.top
        xl = x1 - x0
        yl = y1 - y0
        m = max(1, int(math.floor(yl / self.pattern_width)))
        pw = yl / m
        ps = self.pattern_slant * (pw / self.pattern_width)
        n = int(math.ceil(xl / pw))
        for i in range(n):
            if i % 2 == 0:
                c.setFillColor(fc)
                c.setStrokeColor(fc)
            else:
                continue
            xi = x0 + i * pw
            xi0 = xi + ps
            xi1 = xi0 + pw
            xi2 = xi + pw
            m = (y1 - y0) / ps
            p = c.beginPath()
            p.moveTo(xi, y0)
            if xi0 > x1:
                yi = y0 + m * (x1 - xi)
                p.lineTo(x1, yi)
                p.lineTo(x1, y0)
            elif xi1 > x1:
                p.lineTo(xi0, y1)
                p.lineTo(x1, y1)
                yi = y0 + m * (x1 - xi2)
                p.lineTo(x1, yi)
                p.lineTo(xi2, y0)
            else:
                p.lineTo(xi0, y1)
                p.lineTo(xi1, y1)
                p.lineTo(xi2, y0)
            p.lineTo(xi, y0)
            c.drawPath(p, stroke=0, fill=1)

    def _draw_squares(self, c, fc):
        mrect = self.style.get_margin_rect(self.rect)
        x0, x1 = mrect.left, mrect.right
        y0, y1 = mrect.bottom, mrect.top
        xl = x1 - x0
        yl = y1 - y0
        m = max(1, int(math.floor(yl / self.pattern_width)))
        pw = yl / m
        n = int(math.floor(xl / pw))
        for j in range(m):
            for i in range(n):
                if (j + i) % 2 == 0:
                    c.setFillColor(fc)
                    c.setStrokeColor(fc)
                else:
                    continue
                xi = x0 + i * pw
                yi = y0 + j * pw
                p = c.beginPath()
                p.moveTo(xi, yi)
                p.lineTo(xi, yi + pw)
                p.lineTo(xi + pw, yi + pw)
                p.lineTo(xi + pw, yi)
                p.lineTo(xi, yi)
                c.drawPath(p, stroke=0, fill=1)

    def draw_pattern_rect(self, c):
        bc = rl_colour(self.background_colour)
        fc = rl_colour(self.foreground_colour)
        mrect = self.style.get_margin_rect(self.rect)
        c.setFillColor(bc)
        c.setStrokeColor(bc)
        c.setLineWidth(0.1)
        c.rect(
            mrect.left, mrect.bottom, mrect.width, mrect.height, stroke=0, fill=1,
        )
        if self.pattern == "slant-line":
            self._draw_slant_line(c, fc)
        elif self.pattern == "squares":
            self._draw_squares(c, fc)
