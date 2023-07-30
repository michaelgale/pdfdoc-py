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
# Styled line

from toolbox import *
from pdfdoc import *


class StyledLine:
    """Draws an arrow head with arbitrary style. The arrow can be placed
    and rotated in direction 0-360 deg."""

    def __init__(self, style):
        self.style = DocStyle()
        self.style.set_with_dict(style)

    def __repr__(self):
        return "%s()" % (self.__class__.__name__,)

    @property
    def line_width(self):
        return self.style["line-width"]

    @property
    def dash(self):
        return self.style["line-dash"]

    def arrow_head(self, c, xo, yo, angle=0):
        aw = self.style["arrow-width"]
        al = self.style["arrow-length"]
        canvas_save_state(c, xo, yo, angle)
        p = c.beginPath()
        p.moveTo(al, -aw)
        p.lineTo(0, 0)
        p.lineTo(al, aw)
        c.drawPath(p, stroke=1, fill=0)
        c.restoreState()

    def draw_in_canvas(self, c, x0, y0, x1, y1, arrow0=False, arrow1=False):
        if isinstance(self.dash, list):
            c.setDash(array=self.dash)
        elif self.dash is not None:
            c.setDash(*self.dash)
        rc = rl_colour(self.style["line-colour"])
        c.setStrokeColor(rc)
        c.setLineWidth(self.line_width)
        p = c.beginPath()
        p.moveTo(x0, y0)
        p.lineTo(x1, y1)
        c.drawPath(p, stroke=1, fill=0)
        if arrow0:
            xl = x1 - x0
            yl = y1 - y0
            angle = degrees(atan2(yl, xl))
            self.arrow_head(c, x0, y0, angle=angle)
        if arrow1:
            xl = x0 - x1
            yl = y0 - y1
            angle = degrees(atan2(yl, xl))
            self.arrow_head(c, x1, y1, angle=angle)
        c.setDash([])

    @staticmethod
    def draw_line(
        c,
        x0,
        y0,
        x1,
        y1,
        line_width=None,
        arrow0=False,
        arrow1=False,
        dash=None,
        style=None,
    ):
        line = StyledLine(style=style)
        if line_width is not None:
            line.style["line-width"] = line_width
        if dash is not None:
            line.style["line-dash"] = dash
        line.draw_in_canvas(c, x0, y0, x1, y1, arrow0, arrow1)

    @staticmethod
    def draw_arc(c, x0, y0, radius, a0, a1, line_width=None, dash=None, style=None):
        line = StyledLine(style=style)
        if line_width is not None:
            line.style["line-width"] = line_width
        if dash is not None:
            c.setDash(dash)
        c.setLineWidth(line.style["line-width"])
        rc = rl_colour(line.style["line-colour"])
        c.setStrokeColor(rc)
        p = c.beginPath()
        p.arc(
            x0 - radius,
            y0 - radius,
            x0 + radius,
            y0 + radius,
            startAng=a0,
            extent=(a1 - a0),
        )
        c.drawPath(p, stroke=1, fill=0)
        c.setDash([])

    @staticmethod
    def draw_grid(c, xo, yo, xs, ys, nx, ny, style=None):
        line = StyledLine(style=style)
        c.setLineWidth(line.style["grid-line-width"])
        rc = rl_colour(line.style["grid-line-colour"])
        c.setStrokeColor(rc)
        if isinstance(line.style["grid-dash"], list):
            c.setDash(array=line.style["grid-dash"])
        else:
            c.setDash(*line.style["grid-dash"])
        yc = yo + ny * ys
        for x in range(nx + 1):
            p = c.beginPath()
            xc = xo + x * xs
            p.moveTo(xc, yo)
            p.lineTo(xc, yc)
            c.drawPath(p, stroke=1, fill=0)
        xc = xo + nx * xs
        for y in range(ny + 1):
            p = c.beginPath()
            yc = yo + y * ys
            p.moveTo(xo, yc)
            p.lineTo(xc, yc)
            c.drawPath(p, stroke=1, fill=0)
        c.setDash([])
