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
# SvgRect image cell container class derived from ContentRect

from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg

from toolbox import *
from pdfdoc import *


class SvgRect(ContentRect):
    def __init__(self, w=1, h=1, filename=None, style=None, auto_size=None, **kwargs):
        super().__init__(w, h, style)
        self.filename = filename
        self.auto_size = auto_size if auto_size is not None else True
        self.parse_kwargs(**kwargs)

    def __repr__(self):
        return "%s(%.2f, %.2f, %r)" % (
            self.__class__.__name__,
            self.rect.width,
            self.rect.height,
            self.filename,
        )

    def __str__(self):
        s = []
        s.append("SvgRect: %s" % (self.rect))
        s.append("  filename: %s" % (self.filename))
        return "\n".join(s)

    def draw_in_canvas(self, c):
        self.draw_rect(c)
        self.draw_svg_rect(c)
        self.draw_overlay_content(c)
        if self.show_debug_rects:
            self.draw_debug_rect(c, self.rect)
            inset_rect = self.style.get_inset_rect(self.rect)
            self.draw_debug_rect(c, inset_rect, (0, 0, 1))

    def get_content_size(self, with_padding=True):
        if self.filename is None:
            return 0, 0
        if self.filename == "":
            return 0, 0
        dwg = svg2rlg(self.filename)
        return super().get_content_size(
            dwg.minWidth(), dwg.height, with_padding=with_padding
        )

    def draw_svg_rect(self, c):
        if self.filename is None:
            return
        if self.filename == "":
            return
        dwg = svg2rlg(self.filename)
        (iw, ih) = dwg.minWidth(), dwg.height
        inset_rect = self.style.get_inset_rect(self.rect)
        if self.auto_size:
            tw, th = Rect.get_best_rect_metrics(
                iw, ih, inset_rect.width, inset_rect.height
            )
        else:
            tw, th = iw, ih
        dwg.scale(tw / iw, th / ih)
        tx, ty = self.aligned_corner(tw, th)
        renderPDF.draw(dwg, c, tx, ty)
