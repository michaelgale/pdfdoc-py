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


class TextRect(ContentRect):
    def __init__(self, w=1, h=1, withText="", style=None):
        super().__init__(w, h, style)
        self.text = withText
        self.clip_text = False
        self.trim_callback = None
        self.split_lines = True
        self.detect_fractions = True

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
    def font(self):
        return self.style["font-name"]

    @font.setter
    def font(self, font_name):
        self.style["font-name"] = font_name

    @property
    def font_size(self):
        return self.style["font-size"]

    @font_size.setter
    def font_size(self, font_size):
        self.style["font-size"] = font_size

    @property
    def font_colour(self):
        return self.style["font-colour"]

    @font_colour.setter
    def font_colour(self, colour):
        self.style["font-colour"] = colour

    def get_content_size(self, with_padding=True):
        c = canvas.Canvas("tmp.pdf")
        c.saveState()
        font_name = self.style["font-name"]
        font_size = self.style["font-size"]
        try:
            c.setFont(font_name, font_size)
        except:
            c.setFont(DEF_FONT_NAME, font_size)
        tw, th = get_string_metrics(c, self.text, font_name, font_size)
        ta, _ = get_string_asc_des(c, self.text, font_name, font_size)
        th += ta
        tw += self.style.width_pad_margin
        tw *= 1.05
        c.restoreState()
        return super().get_content_size(tw, th, with_padding=with_padding)

    def draw_in_canvas(self, c):
        self.draw_rect(c)
        self.draw_text(c)
        if self.overlay_content is not None:
            self.overlay_content.draw_in_canvas(c)
        if self.show_debug_rects:
            self.draw_debug_rect(c, self.rect)
            inset_rect = self.style.get_inset_rect(self.rect)
            self.draw_debug_rect(c, inset_rect, (0, 0, 1))

    def draw_text(self, c):
        font_name = self.font
        font_size = self.font_size
        try:
            c.setFont(font_name, font_size)
        except:
            c.setFont(DEF_FONT_NAME, font_size)
        _, th = get_string_metrics(c, self.text, font_name, font_size)
        tx = self.rect.left
        font_colour = rl_colour(self.style["font-colour"])
        c.setFillColor(font_colour)
        c.setStrokeColor(font_colour)
        text_width = self.rect.width - self.style.width_pad_margin
        if self.trim_callback is not None:
            textLabel = self.trim_callback(c, self.text, self)
        elif self.clip_text:
            textLabel = trim_string_to_fit(
                c, self.text, font_name, font_size, text_width
            )
        else:
            textLabel = self.text
        inset_rect = self.style.get_inset_rect(self.rect)
        if self.split_lines:
            lines = split_string_to_fit(c, textLabel, font_name, font_size, text_width)
        else:
            lines = [textLabel]
        ls = 1.0 + self.style["line-spacing"]
        cy = (len(lines) - 1) * (th / 2) * ls
        for i, line in enumerate(lines):
            if self.vert_align == "centre":
                _, ty = inset_rect.get_centre()
                if len(lines) == 1:
                    ty -= th / 2
                else:
                    ty = ty + cy - th / 2 - (i * th * ls)
            elif self.vert_align == "top":
                ty = inset_rect.top - th - (i * th * ls)
            else:
                if len(lines) == 1:
                    ty = inset_rect.bottom + cy
                else:
                    ty = inset_rect.bottom + cy - ((i - 1) * th * ls)

            if self.horz_align == "centre":
                tx, _ = inset_rect.get_centre()
                c.drawCentredString(tx, ty, line)
            elif self.horz_align == "right":
                tx = inset_rect.right
                c.drawRightString(tx, ty, line)
            else:
                tx = inset_rect.left
                c.drawString(tx, ty, line)
