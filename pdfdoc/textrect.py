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
# PDF text rectangle class

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
from docstyle import *

class TextRect:
    def __init__(self, w, h, withText, style=None):
        self.rect = Rect()
        self.rect.set_size(w, h)
        self.text = withText
        self.clip_text = False
        self.style = DocStyle()
        if style is not None:
            self.style.set_with_dict(style)

    def draw_in_canvas(self, c):
        self.draw_rect(c)
        self.draw_text(c)

    def draw_rect(self, c):
        has_background = self.style.get_attr("background-fill", False)
        background_colour = self.style.get_attr("background-colour", (1, 1, 1))
        if has_background:
            fc = rl_colour(background_colour)
        else:
            fc = rl_colour_trans()
        c.setFillColor(fc)
        has_border = self.style.get_attr("border-outline", False)
        if border_outline:
            border_colour = self.style.get_attr("border-colour", (1, 1, 1))
            border_width = self.style.get_attr("border-width", 0)
            rc = rl_colour(border_colour)
            c.setStrokeColor(rc)
            c.setLineWidth(border_width)

        c.rect(
            self.rect.left,
            self.rect.bottom,
            self.rect.width,
            self.rect.height,
            stroke=int(has_border),
            fill=int(has_background)
        )

    def draw_text(self, c):
        font_name = self.style.get_attr("font-name", DEF_FONT_NAME)
        font_size = self.style.get_attr("font-size", DEF_FONT_SIZE)
        c.setFont(font_name, font_size)
        tw, th = GetStringMetrics(c, self.text, font_name, font_size)
        tx = self.rect.left
        font_colour = rl_colour(self.style.get_attr("font-colour", (0, 0, 0)))
        c.setFillColor(font_colour)
        c.setStrokeColor(font_colour)
        text_width = self.rect.width - self.style.get_width_trim()
        if self.clip_text:
            textLabel = TrimStringToFit(
                c,
                self.text,
                self.font_name,
                self.font_size,
                text_width,
            )
        else:
            textLabel = self.text

        vert_align = self.style.get_attr("vert-align", "centre")
        if vert_align == "centre":
            tmp, ty = self.rect.get_centre()
            ty -= th / 2.0
        elif vert_align == "top":
            ty = self.rect.top - self.vert_padding - th
        else:
            ty = self.rect.bottom + self.vert_padding

        horz_align = self.style.get_attr("horz-align", "centre")
        if horz_align == "centre":
            tx, tmp = self.rect.get_centre()
            c.drawCentredString(tx, ty, textLabel)
        elif horz_align == "right":
            tx = self.rect.right - self.style.get_right_trim()
            c.drawRightString(tx, ty, textLabel)
        else:
            tx = self.rect.left + self.style.get_left_trim()
            c.drawString(tx, ty, textLabel)
