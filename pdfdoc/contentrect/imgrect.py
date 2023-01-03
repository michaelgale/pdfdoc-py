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


class ImageRect(ContentRect):
    def __init__(self, w=1, h=1, filename="", style=None, dpi=None, auto_size=None):
        super().__init__(w, h, style)
        self.filename = filename
        self.auto_size = auto_size if auto_size is not None else True
        self.dpi = dpi if dpi is not None else 300

    def draw_in_canvas(self, c):
        self.draw_rect(c)
        self.draw_image_rect(c)
        if self.overlay_content is not None:
            self.overlay_content.draw_in_canvas(c)
        if self.show_debug_rects:
            self.draw_debug_rect(c, self.rect)
            inset_rect = self.style.get_inset_rect(self.rect)
            self.draw_debug_rect(c, inset_rect, (0, 0, 1))

    def get_content_size(self, with_padding=True):
        if self.filename == "":
            return 0, 0
        (iw, ih) = get_image_metrics(self.filename)
        tw, th = iw / self.dpi * 72, ih / self.dpi * 72
        if with_padding:
            tw += self.style.get_width_trim()
            th += self.style.get_height_trim()
        w = self.fixed_rect.width if self.is_fixed_width else tw
        h = self.fixed_rect.height if self.is_fixed_height else th
        return w, h

    def draw_image_rect(self, c):
        if self.filename == "":
            return
        (iw, ih) = get_image_metrics(self.filename)
        inset_rect = self.style.get_inset_rect(self.rect)
        if self.auto_size:
            tw, th = self.get_best_rect_metrics(
                iw, ih, inset_rect.width, inset_rect.height
            )
        else:
            tw, th = iw / self.dpi * 72, ih / self.dpi * 72
        vert_align = self.style["vert-align"]
        if vert_align == "centre":
            _, ty = inset_rect.get_centre()
            ty -= th / 2.0
        elif vert_align == "top":
            ty = inset_rect.top - th
        else:
            ty = inset_rect.bottom

        horz_align = self.style["horz-align"]
        if horz_align == "centre":
            tx, _ = inset_rect.get_centre()
            tx -= tw / 2.0
        elif horz_align == "right":
            tx = inset_rect.right
            tx -= tw
        else:
            tx = inset_rect.left
        c.setFillColor(rl_colour((0, 0, 0)))
        c.drawImage(self.filename, tx, ty, tw, th, mask="auto")

    @staticmethod
    def get_best_rect_metrics(fromWidth, fromHeight, inWidth, inHeight):
        if fromWidth < 1e-3 or fromHeight < 1e-3:
            return 0, 0
        if fromWidth > fromHeight:
            bestHeight = inHeight
            bestWidth = (inHeight / fromHeight) * fromWidth
        else:
            bestWidth = inWidth
            bestHeight = (inWidth / fromWidth) * fromHeight
        if bestHeight > inHeight:
            scale = inHeight / bestHeight
            bestHeight *= scale
            bestWidth *= scale
        if bestWidth > inWidth:
            scale = inWidth / bestWidth
            bestHeight *= scale
            bestWidth *= scale
        return bestWidth, bestHeight
