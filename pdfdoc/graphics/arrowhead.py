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
# Draws a styled arrow head shape

from math import sin, cos
from toolbox import *
from pdfdoc import *
from pdfdoc.helpers import linear_offset, line_angle


class ArrowHead(DocStyleMixin):
    """Draws an arrow head with arbitrary style. The arrow can be placed
    and rotated in direction 0-360 deg.
    The arrow styles supported are:
      - flat, taper, stick, dimension, cap
    """

    def __init__(self, style=None):
        self.style = DocStyle()
        # default size if not set
        self.style["length"] = 0.2 * inch
        self.style["width"] = 0.12 * inch
        if style is not None:
            self.style.set_with_dict(style)
        self.taper = 0.15

    def __repr__(self):
        return "%s()" % (self.__class__.__name__,)

    def draw_in_canvas(self, c, pt, dir=0, tip_origin=False):
        """Draw the arrow head at coordinate 'pt' facing in direction 'dir'
        if tip_origin is True, then the arrow head tip is coincident with
        'pt', otherwise it is centred on 'pt'
        """
        assert self.arrow_style in ("flat", "taper", "stick", "dimension", "cap")
        c.saveState()
        al2 = self.style["length"] / 2
        aw2 = self.style["width"] / 2
        tl = 0
        if self.arrow_style == "taper":
            tl = self.taper * al2
        elif self.arrow_style == "flat":
            tl = 0
        st = 1 if self.border_outline else 0
        c.translate(pt[0], pt[1])
        c.rotate(dir)
        c.setLineWidth(self.border_width)
        c.setFillColor(self.line_colour)
        c.setStrokeColor(self.border_colour)
        c.setLineCap(0)
        p = c.beginPath()
        if tip_origin:
            x0, x1 = 0, -2 * al2
        else:
            x0, x1 = al2, -al2
        if self.arrow_style in ("stick", "dimension"):
            c.setStrokeColor(self.line_colour)
            dx = linear_offset(2 * al2, aw2, self.line_width)
            p.moveTo(x0, 0)
            p.lineTo(x1, aw2)
            p.lineTo(x1, aw2 - self.line_width)
            p.lineTo(x0 - dx, 0)
            p.lineTo(x1, -aw2 + self.line_width)
            p.lineTo(x1, -aw2)
            p.lineTo(x0, 0)
            c.drawPath(p, stroke=st, fill=1)
            if self.arrow_style == "dimension":
                c.setLineWidth(self.line_width)
                aw2 += self.line_width / 4
                p = c.beginPath()
                p.moveTo(x0, aw2)
                p.lineTo(x0, -aw2)
                c.drawPath(p, stroke=1, fill=0)
        elif self.arrow_style == "cap":
            p.moveTo(x0, 0)
            p.lineTo(x1, aw2)
            p.lineTo(x1, -aw2)
            p.lineTo(x0, 0)
            c.drawPath(p, stroke=st, fill=1)
        else:
            p.moveTo(x0, 0)
            p.lineTo(x1, aw2)
            p.lineTo(x1 + tl, 0)
            p.lineTo(x1, -aw2)
            p.lineTo(x0, 0)
            p.lineTo(x1, aw2)
            c.drawPath(p, stroke=st, fill=1)
        c.restoreState()

    def tip_offset(self, p0, p1, line_width):
        return self.line_tip_offset(p0, p1, line_width, self.length, self.width)

    @staticmethod
    def line_tip_offset(p0, p1, line_width, tip_length, tip_width):
        """Offsets a line from p1 to p0 where end coordinate p0 has
        an arrow head with dimensions tip_length, tip_width."""
        if tip_width <= line_width:
            dx = tip_length
        else:
            hw, hlw = tip_width / 2, line_width / 2
            dx = linear_offset(tip_length, hw, hlw)
        line_th = line_angle(p0, p1, degrees=False)
        xo, yo = p0[0] + dx * cos(line_th), p0[1] + dx * sin(line_th)
        return xo, yo
