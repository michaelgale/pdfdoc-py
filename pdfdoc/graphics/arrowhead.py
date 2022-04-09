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
# ImageRect image cell container class derived from ContentRect

from toolbox import *
from pdfdoc import *


class ArrowHead:
    """Draws an arrow head with arbitrary style. The arrow can be placed
    and rotated in direction 0-360 deg."""

    def __init__(self, style):
        self.style = DocStyle()
        self.style.set_with_dict(style)
        self.taper = 0.15

    def draw_in_canvas(self, c, pt, dir=0):
        al2 = self.style.get_attr("length") / 2
        aw2 = self.style.get_attr("width") / 2
        fc = self.style.get_attr("border-colour")
        bc = self.style.get_attr("line-colour")
        tl = 0
        if self.style.get_attr("arrow-style") == "taper":
            tl = self.taper * al2
        if self.style.get_attr("arrow-style") == "flat":
            tl = 0
        st = 1 if self.style.get_attr("border-outline") else 0
        c.saveState()
        c.translate(pt[0], pt[1])
        c.rotate(dir)
        c.setLineWidth(self.style.get_attr("border-width"))
        c.setFillColor(bc)
        c.setStrokeColor(fc)
        c.setLineCap(0)
        p = c.beginPath()
        x, y = pt[0], pt[1]
        p.moveTo(al2, 0)
        p.lineTo(-al2, aw2)
        p.lineTo(-al2 + tl, 0)
        p.lineTo(-al2, -aw2)
        p.lineTo(al2, 0)
        p.lineTo(-al2, aw2)
        c.drawPath(p, stroke=st, fill=1)
        c.restoreState()
