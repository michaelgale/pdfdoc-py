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
# Generic ContentRect parent container class

from toolbox import *
from pdfdoc import *


class ContentRect:
    def __init__(self, w=1, h=1, style=None, **kwargs):
        self.rect = Rect(w, h)
        self.style = DocStyle()
        if style is not None:
            self.style.set_with_dict(style)
        self.show_debug_rects = False
        self.overlay_content = None
        self.is_fixed_width = False
        self.is_fixed_height = False
        self.fixed_rect = Rect(w, h)
        self.parse_kwargs(**kwargs)

    def __repr__(self):
        return "%s(%.2f, %.2f)" % (
            self.__class__.__name__,
            self.rect.width,
            self.rect.height,
        )

    def __str__():
        return "Content Rect: %s" % (self.rect)

    def parse_kwargs(self, **kwargs):
        for k, v in kwargs.items():
            if k in self.__dict__:
                self.__dict__[k] = v

    @property
    def bottom_left(self):
        return self.rect.get_bottom_left()

    @bottom_left.setter
    def bottom_left(self, pos):
        if not isinstance(pos, Point):
            self.rect.move_bottom_left_to(Point(*pos))
        else:
            self.rect.move_bottom_left_to(pos)

    @property
    def top_left(self):
        return self.rect.get_top_left()

    @top_left.setter
    def top_left(self, pos):
        if not isinstance(pos, Point):
            self.rect.move_top_left_to(Point(*pos))
        else:
            self.rect.move_top_left_to(pos)

    @property
    def centre(self):
        return self.rect.centre

    @centre.setter
    def centre(self, pos):
        if not isinstance(pos, Point):
            self.rect.move_to(Point(*pos))
        else:
            self.rect.move_to(pos)

    @property
    def size(self):
        return self.rect.get_size()

    @size.setter
    def size(self, new_size):
        self.rect.set_size(*new_size)

    @property
    def horz_align(self):
        return self.style["horz-align"]

    @horz_align.setter
    def horz_align(self, alignment):
        self.style["horz-align"] = alignment

    @property
    def vert_align(self):
        return self.style["vert-align"]

    @vert_align.setter
    def vert_align(self, alignment):
        self.style["vert-align"] = alignment

    @property
    def background_colour(self):
        return self.style["background-colour"]

    @background_colour.setter
    def background_colour(self, colour=None):
        if colour is None:
            self.style["background-fill"] = False
        else:
            self.style["background-fill"] = True
            self.style["background-colour"] = colour

    @property
    def border_colour(self):
        return self.style["border-colour"]

    @border_colour.setter
    def border_colour(self, colour=None):
        if colour is None:
            self.style["border-outline"] = False
        else:
            self.style["border-colour"] = colour

    @property
    def border_width(self):
        return self.style["border-width"]

    @border_width.setter
    def border_width(self, width=None):
        if width is None:
            self.style["border-outline"] = False
        else:
            self.style["border-width"] = width

    @property
    def border_outline(self):
        return self.style["border-outline"]

    @border_outline.setter
    def border_outline(self, show=False):
        if isinstance(show, str):
            if "top" in show.lower():
                self.style["border-line-top"] = True
            if "bottom" in show.lower():
                self.style["border-line-bottom"] = True
            if "left" in show.lower():
                self.style["border-line-left"] = True
            if "right" in show.lower():
                self.style["border-line-right"] = True
            if "all" in show.lower():
                self.style["border-outline"] = True
            if "none" in show.lower():
                self.style["border-outline"] = False
                self.style["border-line-top"] = False
                self.style["border-line-bottom"] = False
                self.style["border-line-left"] = False
                self.style["border-line-right"] = False
        else:
            self.style["border-outline"] = show

    def draw_debug_rect(self, c, r, colour=(0, 0, 0)):
        c.saveState()
        c.setFillColor(rl_colour_trans())
        c.setStrokeColor(rl_colour(colour))
        c.setLineWidth(0.1)
        c.rect(r.left, r.bottom, r.width, r.height, stroke=True, fill=False)
        c.restoreState()

    def draw_overlay_content(self, c):
        if self.overlay_content is not None:
            self.overlay_content.rect = self.rect
            self.overlay_content.draw_in_canvas(c)

    def draw_in_canvas(self, c):
        self.draw_rect(c)
        self.draw_overlay_content(c)
        if self.show_debug_rects:
            self.draw_debug_rect(c, self.rect)
            inset_rect = self.style.get_inset_rect(self.rect)
            self.draw_debug_rect(c, inset_rect, (0, 0, 1))

    def set_fixed_size(self, w, h):
        self.is_fixed_height = True
        self.is_fixed_width = True
        self.fixed_rect = Rect(w, h)

    def get_content_size(self, width=None, height=None, with_padding=None):
        width = self.rect.width if width is None else width
        height = self.rect.height if height is None else height
        if with_padding is not None and with_padding:
            width += self.style.width_pad_margin
            height += self.style.height_pad_margin
        w = self.fixed_rect.width if self.is_fixed_width else width
        h = self.fixed_rect.height if self.is_fixed_height else height
        return w, h

    def draw_rect(self, c):
        rl_draw_rect(c, self.rect, self.style)

    def aligned_corner(self, width, height):
        """Returns the coordinate of the top left corner of the content within a
        cell, respecting the style's vertical and horizontal alignment."""
        inset_rect = self.style.get_inset_rect(self.rect)
        if self.vert_align == "centre":
            _, ty = inset_rect.get_centre()
            ty -= height / 2.0
        elif self.vert_align == "top":
            ty = inset_rect.top - height
        else:
            ty = inset_rect.bottom
        if self.horz_align == "centre":
            tx, _ = inset_rect.get_centre()
            tx -= width / 2.0
        elif self.horz_align == "right":
            tx = inset_rect.right
            tx -= width
        else:
            tx = inset_rect.left
        return tx, ty


class FixedRect(ContentRect):
    """Convenience class to delcare a fixed sized rectangle."""

    def __init__(self, w=1, h=1, style=None):
        self.rect = Rect(w, h)
        self.style = DocStyle()
        if style is not None:
            self.style.set_with_dict(style)
        self.show_debug_rects = False
        self.overlay_content = None
        self.is_fixed_width = True
        self.is_fixed_height = True
        self.fixed_rect = Rect(w, h)

    def __repr__(self):
        return "%s(%.2f, %.2f)" % (
            self.__class__.__name__,
            self.rect.width,
            self.rect.height,
        )

    def __str__():
        return "FixedRect: %s" % (self.rect)
