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
# PDF document utilities

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

from pdfdoc import *

attr_aliases = {
  "title-color": "title-colour",
  "line-color": "line-colour",
  "font-color": "font-colour",
  "border-color": "border-colour",
  "background-color": "background-colour",
  "horz-align": "horizontal-align",
  "vert-align": "vertical-align"
}

class DocStyle:
    def __init__(self):
        self.attr = {
            "width": 0,
            "height": 0,
            "left-margin": 0,
            "right-margin": 0,
            "top-margin": 0,
            "bottom-margin": 0,
            "ncolumns": 0,
            "nrows": 0,
            "top-padding": 0,
            "bottom-padding": 0,
            "left-padding": 0,
            "right-padding": 0,
            "cell-padding": 0,
            "text-baseline": 0,
            "gutter-width": 0,
            "title-width": 0,
            "title-height": 0,
            "title-font": "",
            "title-colour": (0, 0, 0),
            "title-font-size": 0,
            "font": "",
            "font-colour": (0, 0, 0),
            "font-size": 0,
            "line-width": 0,
            "line-colour": (0, 0, 0),
            "border-width": 0,
            "border-colour": (0, 0, 0),
            "background-colour": (0, 0, 0),
            "background-fill": False,
            "border-outline": False,
            "vert-align": "centre",
            "horz-align": "centre",
        }

    def add_attr(self, attr_name, attr_value=None):
        self.attr[attr_name] = attr_value

    def get_attr(self, attr_name, def_value=None):
        if attr_name in self.attr:
            return self.attr[attr_name]
        if attr_name is attr_aliases:
            alias = attr_aliases[attr_name]
            if alias in self.attr:
                return self.attr[alias]
        return def_value

    def set_with_dict(self, dict):
        for key, value in dict.items():
            if key in self.attr:
                self.attr[key] = value

    def get_width_trim(self):
        return (
          self.get_attr("left-margin", 0)
          + self.get_attr("right-margin", 0)
          + self.get_attr("left-padding", 0)
          + self.get_attr("right-padding", 0)
        )

    def get_height_trim(self):
        return (
          self.get_attr("top-margin", 0)
          + self.get_attr("bottom-margin", 0)
          + self.get_attr("top-padding", 0)
          + self.get_attr("bottom-padding", 0)
        )

    def get_right_trim(self):
        return (
          self.get_attr("right-margin", 0)
          + self.get_attr("right-padding", 0)
        )

    def get_left_trim(self):
        return (
          self.get_attr("left-margin", 0)
          + self.get_attr("left-padding", 0)
        )

    def get_top_trim(self):
        return (
          self.get_attr("top-margin", 0)
          + self.get_attr("top-padding", 0)
        )

    def get_bottom_trim(self):
        return (
          self.get_attr("bottom-margin", 0)
          + self.get_attr("bottom-padding", 0)
        )

    def get_inset_rect(self, fromRect):
        inset_rect = copy.copy(fromRect)
        inset_rect.left += self.get_left_trim()
        inset_rect.right -= self.get_right_trim()
        inset_rect.top -= self.get_top_trim()
        inset_rect.bottom += self.get_bottom_trim()
        inset_rect.get_size()
        return inset_rect
