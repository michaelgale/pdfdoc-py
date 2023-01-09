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
# Generic ContentRect parent container class

from toolbox import *
from pdfdoc import *


class ContentRect:
    def __init__(self, w=1, h=1, style=None):
        self.rect = Rect(w, h)
        self.style = DocStyle()
        if style is not None:
            self.style.set_with_dict(style)
        self.show_debug_rects = False
        self.overlay_content = None
        self.is_fixed_width = False
        self.is_fixed_height = False
        self.fixed_rect = Rect(w, h)

    def __repr__(self):
        return "%s(%.2f, %.2f)" % (
            self.__class__.__name__,
            self.rect.width,
            self.rect.height,
        )

    def __str__():
        return "Content Rect: %s" % (self.rect)

    @property
    def top_left(self):
        return self.rect.get_top_left()

    @top_left.setter
    def top_left(self, pos):
        self.rect.move_top_left_to(Point(*pos))

    @property
    def size(self):
        return self.rect.get_size()

    @size.setter
    def size(self, new_size):
        self.rect.set_size(*new_size)

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

    def set_fixed_size(self, w, h):
        self.is_fixed_height = True
        self.is_fixed_width = True
        self.fixed_rect = Rect(w, h)

    def get_content_size(self):
        w = self.fixed_rect.width if self.is_fixed_width else self.rect.width
        h = self.fixed_rect.height if self.is_fixed_height else self.rect.height
        return w, h

    def draw_rect(self, c):
        has_background = self.style["background-fill"]
        background_colour = self.style["background-colour"]
        if has_background:
            fc = rl_colour(background_colour)
            c.setFillColor(fc)
        else:
            fc = rl_colour_trans()
        rl_set_border_stroke(c, self.style)
        mrect = self.style.get_margin_rect(self.rect)
        border_radius = self.style["border-radius"]
        if border_radius > 0:
            c.roundRect(
                mrect.left,
                mrect.bottom,
                mrect.width,
                mrect.height,
                radius=border_radius,
                stroke=self.style["border-outline"],
                fill=has_background,
            )
        else:
            c.rect(
                mrect.left,
                mrect.bottom,
                mrect.width,
                mrect.height,
                stroke=self.style["border-outline"],
                fill=has_background,
            )
