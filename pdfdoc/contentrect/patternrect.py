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
# Pattern filled ContentRect derived class

import math

from toolbox import *
from pdfdoc import *


class PatternRect(ContentRect):
    def __init__(self, w=1, h=1, pattern=None, style=None, **kwargs):
        super().__init__(w, h, style=style)
        self.pattern = "slant-line"
        if pattern is not None:
            self.pattern = pattern
        self.pattern_width = 18.0
        self.pattern_slant = 18.0
        self.background_colour = (1, 1, 1)
        self.foreground_colour = (1, 0, 0)
        self.parse_kwargs(**kwargs)

    def __repr__(self):
        return "%s(%.2f, %.2f, %r)" % (
            self.__class__.__name__,
            self.rect.width,
            self.rect.height,
            self.pattern,
        )

    def __str__(self):
        s = []
        s.append("PatternRect: %s" % (self.rect))
        s.append("  pattern: %s" % (self.pattern))
        return "\n".join(s)

    def draw_in_canvas(self, c):
        self.draw_rect(c)
        self.draw_pattern_rect(c)
        self.draw_overlay_content(c)
        if self.show_debug_rects:
            self.draw_debug_rect(c, self.rect)
            self.draw_debug_rect(c, self.inset_rect, (0, 0, 1))

    def _draw_slant_line(self, c, fc):
        mrect = self.margin_rect
        x0, x1 = mrect.left, mrect.right
        y0, y1 = mrect.bottom, mrect.top
        xl = x1 - x0
        yl = y1 - y0
        xp = max(1, int(math.ceil(xl / self.pattern_width)))
        xs = xl / xp
        xh = xs / 2
        yp = max(1, int(math.ceil(yl / self.pattern_slant)))
        ys = yl / yp

        def _left_tri(xo, yo, xl, yl):
            p = c.beginPath()
            p.moveTo(xo, yo)
            p.lineTo(xo, yo + yl)
            p.lineTo(xo + xl, yo + yl)
            p.moveTo(xo, yo)
            c.drawPath(p, stroke=0, fill=1)

        def _right_tri(xo, yo, xl, yl):
            p = c.beginPath()
            p.moveTo(xo, yo)
            p.lineTo(xo + xl, yo + yl)
            p.lineTo(xo + xl, yo)
            p.moveTo(xo, yo)
            c.drawPath(p, stroke=0, fill=1)

        c.setFillColor(fc)
        c.setStrokeColor(fc)
        for i in range(xp):
            for j in range(yp):
                xi = x0 + i * xs
                yi = y0 + j * ys
                if j % 2 == 0:
                    _left_tri(xi, yi, xh, ys)
                    _right_tri(xi + xh, yi, xh, ys)
                else:
                    _right_tri(xi, yi, xh, ys)
                    _left_tri(xi + xh, yi, xh, ys)

    def _draw_squares(self, c, fc):
        mrect = self.margin_rect
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
        mrect = self.margin_rect
        c.setFillColor(bc)
        c.setStrokeColor(bc)
        c.setLineWidth(0.1)
        c.rect(mrect.left, mrect.bottom, mrect.width, mrect.height, stroke=0, fill=1)
        if self.pattern == "slant-line":
            self._draw_slant_line(c, fc)
        elif self.pattern == "squares":
            self._draw_squares(c, fc)
