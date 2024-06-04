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
# TextRect text cell container class derived from ContentRect

from reportlab.pdfgen import canvas

from toolbox import *
from pdfdoc import *
from pdfdoc.helpers import expand_string_to_fit
from reportlab.lib.colors import Color


class TextRect(ContentRect):
    def __init__(self, w=None, h=None, withText=None, style=None, **kwargs):
        if isinstance(w, (int, float)) and isinstance(h, (int, float)):
            super().__init__(w, h, style)
        else:
            super().__init__(1, 1, style)
        if isinstance(w, str):
            self.text = w
        else:
            self.text = withText if withText is not None else ""
        self.clip_text = False
        self.trim_callback = None
        self.split_lines = False
        self.scale_to_fit = False
        self.expand_to_fit = False
        self._multi_line = False
        self.show_text_bounds = False
        self.parse_kwargs(**kwargs)
        if "icon" in kwargs:
            self.set_icon(kwargs["icon"])

    def __repr__(self):
        return "%s(%.2f, %.2f, %r)" % (
            self.__class__.__name__,
            self.rect.width,
            self.rect.height,
            self.text,
        )

    def __str__(self):
        s = []
        s.append("TextRect: %s" % (self.rect))
        s.append("  Text: %s" % (self.text))
        return "\n".join(s)

    @property
    def is_multi_line(self):
        return self._multi_line

    def set_icon(self, icon_name):
        """Automatically fills a TextRect with an icon from Hazard or FontAwesome fonts"""
        hs = haz_symbol(icon_name)
        if len(hs) > 0:
            self.style["font-name"] = "Hazard"
            self.text = hs
        else:
            self.style["font-name"] = "FontAwesome"
            self.text = fa_symbol(icon_name)

    def get_content_size(self, with_padding=True):
        self._multi_line = False
        text_width = self.rect.width
        font_size = self.font_size
        if self.scale_to_fit:
            font_size = self.style.scale_text_to_fit(self.text, text_width)
        if self.expand_to_fit:
            font_size = self.style.expand_text_to_fit(self.text, text_width)
        if with_padding:
            text_width -= self.style.width_pad_margin
        if self.split_lines and text_width > 0:
            lines = self.style.split_text_to_fit(self.text, text_width, font_size)
        else:
            lines = [self.text]
        max_width = 0
        height = 0
        if len(lines) > 1:
            self._multi_line = True
        for line in lines:
            max_width = max(max_width, self.style.string_width(line, font_size))
            height += self.style.line_height
        return super().get_content_size(max_width, height, with_padding=with_padding)

    def draw_in_canvas(self, c):
        self.snapshot_rect()
        self.draw_rect(c)
        self.draw_text(c)
        self.draw_overlay_content(c)
        if self.show_debug_rects:
            self.draw_debug_rect(c, self.rect)
            self.draw_debug_rect(c, self.inset_rect, DEBUG_INSET_COLOUR)
        self.restore_rect()

    def draw_text(self, c):
        font_size = self.font_size
        font_colour = rl_colour(self.font_colour, self.font_alpha)
        c.setFillColor(font_colour)
        c.setStrokeColor(font_colour)
        text_width = self.rect.width - self.style.width_pad_margin
        if self.trim_callback is not None:
            text = self.trim_callback(c, self.text, self)
        elif self.clip_text:
            text = trim_string_to_fit(c, self.text, self.font, font_size, text_width)
        else:
            text = self.text
            if self.scale_to_fit:
                font_size = self.style.scale_text_to_fit(text, text_width)
            if self.expand_to_fit:
                font_size = self.style.expand_text_to_fit(text, text_width)
        if self.split_lines:
            lines = self.style.split_text_to_fit(text, text_width, font_size)
        else:
            lines = [text]
        single_line = len(lines) == 1
        c.setFont(self.font, font_size)
        cy = (len(lines) - 1) * self.style.line_height
        for i, line in enumerate(lines):
            if self.vert_align == "centre":
                _, ty = self.inset_rect.get_centre()
                if single_line:
                    ty -= self.style.font_height / 2 + self.style.font_descent / 2
                else:
                    ty = (
                        ty
                        + cy / 2
                        - self.style.line_height / 2
                        - self.style.font_descent / 2
                        - (i * self.style.line_height)
                    )
            elif self.vert_align == "top":
                ty = (
                    self.inset_rect.top
                    - self.style.font_descent
                    - ((i + 1) * self.style.line_height)
                )
            else:
                if single_line:
                    ty = self.inset_rect.bottom + cy
                else:
                    ty = (
                        self.inset_rect.bottom + cy - ((i - 1) * self.style.line_height)
                    )
            kern = font_size * self.kerning
            if self.horz_align == "centre":
                tx, _ = self.inset_rect.get_centre()
            elif self.horz_align == "right":
                tx = self.inset_rect.right
            else:
                tx = self.inset_rect.left
            if self.rotation:
                c.saveState()
                c.translate(tx, ty)
                c.rotate(self.rotation)
                tx, ty = 0, 0
            bb = self.style.text_bound_box(line)
            if self.horz_align == "centre":
                c.drawCentredString(tx, ty, line, charSpace=kern)
                bb.move_to(tx, ty + self.style.font_baseline)
            elif self.horz_align == "right":
                c.drawRightString(tx, ty, line, charSpace=kern)
                bb.move_bottom_right_to((tx, ty - self.style.font_baseline))
            else:
                c.drawString(tx, ty, line, charSpace=kern)
                bb.move_bottom_left_to((tx, ty - self.style.font_baseline))
            if self.show_text_bounds:
                c.saveState()
                if c._enforceColorSpace is not None:
                    c.setFillColor(rl_colour((0.1, 0.6, 0.5, 0.0), alpha=0.25))
                else:
                    c.setFillColor(rl_colour((0.9, 0.5, 0.5), 0.25))
                    c.rect(bb.left, bb.bottom, bb.width, bb.height, stroke=0, fill=1)
                c.restoreState()

            if self.rotation:
                c.restoreState()
