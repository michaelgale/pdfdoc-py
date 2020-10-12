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
# Centred container content rect

from reportlab.pdfgen import canvas

from toolbox import *
from pdfdoc import *


class AlignmentRect(ContentRect):
    """ A content container which can force the alignment of its 
    child content cell within its fixed width/height bounds.
    If the child cell's content exceeds this container cell's
    bounds, then it will expand automatically to accommodate. """
    def __init__(self, w, h, style=None):
        super().__init__(w, h, style)
        self.content = None
        self.is_fixed_height = True
        self.is_fixed_width = True

    def __str__():
        s = []
        s.append("Alignment: %s" % (self.rect))
        s.append("  Content: %r" % (self.content))
        return "\n".join(s)


    def draw_in_canvas(self, c):
        self.draw_rect(c)
        self.draw_content_rect(c)
        if self.overlay_content is not None:
            self.overlay_content.draw_in_canvas(c)
        if self.show_debug_rects:
            self.draw_debug_rect(c, self.rect)
            inset_rect = self.style.get_inset_rect(self.rect)
            self.draw_debug_rect(c, inset_rect, (0, 0, 1))

    def rebound_rect(self):
        w, h = self.content.get_content_size()
        self.content.rect.set_size(w, h)
        rc = self.style.get_inset_rect(self.fixed_rect)
        nw = max(w, rc.width)
        nh = max(h, rc.height)
        nw += self.style.get_width_trim()
        nh += self.style.get_height_trim()
        self.rect.set_size_anchored(nw, nh, "top left")         

    def get_content_size(self):
        self.rebound_rect()
        return self.rect.width, self.rect.height       

    def draw_content_rect(self, c):
        w, h = self.content.get_content_size()
        rc = self.style.get_inset_rect(self.rect)
        ha = self.style["horz-align"]
        va = self.style["vert-align"]
        if ha == "left":
            x = rc.left
        elif ha == "right":
            x = rc.right - w
        else:
            x = rc.left + rc.width/2 - w/2
        if va == "top":
            y = rc.top
        elif va == "bottom":
            y = rc.bottom + h
        else:
            y = rc.bottom + rc.height/2 + h/2
        self.content.rect.move_top_left_to((x, y))
        self.content.draw_in_canvas(c)
