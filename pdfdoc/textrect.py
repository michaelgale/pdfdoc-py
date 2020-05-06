#! /usr/bin/env python3
#
# Copyright (C) 2018  Fx Bricks Inc.
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
# TextRect text cell container class derived from ContentRect

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.colors import Color

from fxgeometry import Rect
from pdfdoc import *


class TextRect(ContentRect):
    def __init__(self, w=1, h=1, withText="", style=None):
        super().__init__(w, h, style)
        self.text = withText
        self.clip_text = False
        self.trim_callback = None
        self.split_lines = True

    def __str__(self):
        s = []
        s.append("TextRect: %s" % (self.rect))
        s.append("  Text: %s" % (self.text))
        return "\n".join(s)

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
        font_name = self.style.get_attr("font-name", DEF_FONT_NAME)
        font_size = self.style.get_attr("font-size", DEF_FONT_SIZE)
        try:
            c.setFont(font_name, font_size)
        except:
            c.setFont(DEF_FONT_NAME, font_size)
        tw, th = GetStringMetrics(c, self.text, font_name, font_size)
        _, td = GetStringAscDes(c, self.text, font_name, font_size)
        tx = self.rect.left
        font_colour = rl_colour(self.style.get_attr("font-colour", (0, 0, 0)))
        c.setFillColor(font_colour)
        c.setStrokeColor(font_colour)
        text_width = self.rect.width - self.style.get_width_trim()
        if self.trim_callback is not None:
            textLabel = self.trim_callback(c, self.text, self)
        elif self.clip_text:
            textLabel = TrimStringToFit(
                c, self.text, font_name, font_size, text_width
            )
        else:
            textLabel = self.text
        inset_rect = self.style.get_inset_rect(self.rect)
        vert_align = self.style.get_attr("vert-align", "centre")
        if self.split_lines:
            lines = SplitStringToFit(c, textLabel, font_name, font_size, text_width)
        else:
            lines = [textLabel]
        ls = 1 + self.style.get_attr("line-spacing", 1.1)
        cy = (len(lines) - 1) * (th/2) * ls
        for i, line in enumerate(lines):
            if vert_align == "centre":
                tmp, ty = inset_rect.get_centre()
                if len(lines) == 1:
                    ty -= th/2
                else:
                    ty = ty + cy - th/2 - (i * th * ls)
            elif vert_align == "top":
                ty = inset_rect.top - th - (i * th * ls)
            else:
                if len(lines) == 1:
                    ty = inset_rect.bottom + cy
                else:
                    ty = inset_rect.bottom + cy - ((i-1) * th * ls)

            horz_align = self.style.get_attr("horz-align", "centre")
            if horz_align == "centre":
                tx, tmp = inset_rect.get_centre()
                c.drawCentredString(tx, ty, line)
            elif horz_align == "right":
                tx = inset_rect.right
                c.drawRightString(tx, ty, line)
            else:
                tx = inset_rect.left
                c.drawString(tx, ty, line)
