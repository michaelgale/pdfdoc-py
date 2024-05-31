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
        self.split_lines = True
        self.scale_to_fit = False
        self.expand_to_fit = False
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
        tw += self.kerning * (len(self.text) - 1)
        tw *= 1.05
        c.restoreState()
        return super().get_content_size(tw, th, with_padding=with_padding)

    def draw_in_canvas(self, c):
        self.snapshot_rect()
        self.draw_rect(c)
        self.draw_text(c)
        self.draw_overlay_content(c)
        if self.show_debug_rects:
            self.draw_debug_rect(c, self.rect)
            self.draw_debug_rect(c, self.inset_rect, (0, 0, 1))
        self.restore_rect()

    def draw_text(self, c):
        font_name = self.font
        font_size = self.font_size
        try:
            c.setFont(font_name, font_size)
        except:
            c.setFont(DEF_FONT_NAME, font_size)
            font_name = DEF_FONT_NAME
        font_colour = rl_colour(
            self.style["font-colour"], alpha=self.style["font-alpha"]
        )
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
            if self.scale_to_fit:
                font_size = scale_string_to_fit(
                    c, self.text, font_name, font_size, text_width
                )
                c.setFont(font_name, font_size)
            if self.expand_to_fit:
                font_size = expand_string_to_fit(
                    c, self.text, font_name, font_size, text_width
                )
                c.setFont(font_name, font_size)
        if self.split_lines:
            lines = split_string_to_fit(c, textLabel, font_name, font_size, text_width)
            # check to make sure we didn't split by adding a blank line
            if len(lines) == 2 and "`" not in textLabel:
                if len(lines[0]) == 0:
                    lines = [textLabel]
        else:
            lines = [textLabel]

        _, th = get_string_metrics(c, self.text, font_name, font_size)
        _, descent = get_string_metrics(
            c, self.text, font_name, font_size, with_descent=False
        )
        descent = descent - th
        tx = self.rect.left
        cy = (len(lines) - 1) * th * self.style["line-spacing"]
        line_space = (th + descent) * self.style["line-spacing"]
        single_line = len(lines) == 1
        half = th / 2
        for i, line in enumerate(lines):
            if self.vert_align == "centre":
                _, ty = self.inset_rect.get_centre()
                if single_line:
                    ty -= half
                else:
                    ty = ty + cy - half - (i * line_space) - descent
            elif self.vert_align == "top":
                ty = self.inset_rect.top - th - (i * line_space) - descent
            else:
                if single_line:
                    ty = self.inset_rect.bottom + cy
                else:
                    ty = self.inset_rect.bottom + cy - ((i - 1) * line_space)
            kern = font_size * self.kerning
            rotation = self.style["rotation"]
            if self.horz_align == "centre":
                tx, _ = self.inset_rect.get_centre()
            elif self.horz_align == "right":
                tx = self.inset_rect.right
            else:
                tx = self.inset_rect.left
            if rotation:
                c.saveState()
                c.translate(tx, ty)
                c.rotate(rotation)
                tx, ty = 0, 0
            if self.horz_align == "centre":
                c.drawCentredString(tx, ty, line, charSpace=kern)
            elif self.horz_align == "right":
                c.drawRightString(tx, ty, line, charSpace=kern)
            else:
                c.drawString(tx, ty, line, charSpace=kern)
            if rotation:
                c.restoreState()
