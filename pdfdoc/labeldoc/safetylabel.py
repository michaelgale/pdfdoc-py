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
# Safety Label Class

import math

from reportlab.pdfgen import canvas

from toolbox import *
from pdfdoc import *


class SafetyLabel(TableRow):
    def __init__(self, icon="caution", title="", desc="", colour=None):
        super().__init__(0, 0)
        self.icon = TextRect(0, 0, "", SAFETY_LABEL_ICON, split_lines=False)
        set_icon(icon, self.icon)
        self.icon.font_size = 60
        self.icon2 = TextRect(0, 0, "", SAFETY_LABEL_ICON, split_lines=False)
        self.icon.overlay_content = self.icon2
        self.spacer = ContentRect(0, 0)
        self.icon_column = TableColumn(0, 0)
        self.icon_column.add_row("Icon", self.icon)
        self.icon_column.add_row("Spacer", self.spacer)

        self.title = TextRect(0, 0, title, SAFETY_LABEL_TITLE)
        self.desc = TextRect(0, 0, desc, SAFETY_LABEL_DESC)
        self.text_column = TableColumn(0, 0)
        self.text_column.add_row("Title", self.title)
        self.text_column.add_row("Desc", self.desc)
        self.add_column("Icon", self.icon_column)
        self.add_column("Text", self.text_column)
        self.set_column_width("Icon", 0.22)
        self.set_column_width("Text", AUTO_SIZE)
        if title == "":
            self.set_cell_visible("Text", False)
        if desc == "":
            self.text_column.set_row_height("Title", AUTO_SIZE)
            self.text_column.set_cell_visible("Desc", False)
            self.icon.style.set_attr("vert-align", "top")
            self.icon_column.set_row_height("Icon", AUTO_SIZE)
            self.icon_column.set_cell_visible("Spacer", False)
        else:
            self.text_column.set_row_height("Title", 0.3)
            self.text_column.set_row_height("Desc", AUTO_SIZE)
            self.icon_column.set_row_height("Icon", 0.3)
            self.icon_column.set_row_height("Spacer", AUTO_SIZE)
        self.compute_cell_sizes("width")

        if colour is not None:
            if colour.lower() == "yellow":
                self.set_safety_yellow()
            elif colour.lower() == "red":
                self.set_safety_red()
            elif colour.lower() == "blue":
                self.set_safety_blue()
            elif colour.lower() == "green":
                self.set_safety_green()

    def _get_metrics(self, textrect, c):
        tw, th = get_string_metrics(
            c,
            textrect.text,
            textrect.font,
            textrect.font_size,
            with_descent=False,
        )
        sa, sd = get_string_asc_des(c, textrect.text, textrect.font, textrect.font_size)
        return tw, th, sa, sd

    def _new_height(self, th, sd, th2, sd2):
        if self.icon.overlay_content is not None:
            new_height = max(th - 1.28 * sd, th2 - 1.28 * sd2)
        else:
            if self.icon.font == "Hazard":
                new_height = th - 1.28 * sd
            else:
                new_height = th
        return new_height

    def set_auto_size(self, c, new_size=None):
        if new_size is not None:
            if self.icon.overlay_content is not None:
                self.icon.font_size = 0.9 * new_size
                self.icon2.font_size = new_size
            else:
                self.icon.font_size = new_size

        tw, th, sa, sd = self._get_metrics(self.icon, c)
        tw2, th2, sa2, sd2 = self._get_metrics(self.icon2, c)
        bw = tw / 16
        if self.title.border_outline:
            self.title.border_width = bw
            self.title.style["right-margin"] = bw / 2
            self.title.style.set_tb_margins(bw / 2)
        else:
            self.title.style.set_all_margins(0)
        xw = tw / 4
        self.title.style["left-margin"] = xw
        self.desc.style["left-margin"] = xw
        self.title.style["border-radius"] = 2.5 * bw

        new_width = 1.05 * tw
        xw = tw / 6
        cx, cy = self.rect.get_top_left()
        rw, rh = self.rect.get_size()
        if self.desc.text == "":
            new_height = self._new_height(th, sd, th2, sd2)
            self.text_column.set_row_height("Title", 1)
        else:
            title_height = self._new_height(th, sd, th2, sd2)
            new_height = 2 * title_height + xw
            self.text_column.set_row_height("Title", title_height / new_height)
            self.icon_column.set_row_height("Icon", title_height / new_height)
            self.desc.style["top-margin"] = xw
            self.desc.vert_align = "top"
            self.text_column.set_row_height("Desc", AUTO_SIZE)
            self.icon_column.set_row_height("Spacer", AUTO_SIZE)
            self.spacer.style.set_attr("top-margin", xw)
        self.rect.set_size(rw, new_height)
        self.rect.move_top_left_to((cx, cy))
        self.icon_column.compute_cell_sizes("height")
        self.text_column.compute_cell_sizes("height")
        self.set_column_width("Icon", new_width / rw)
        self.compute_cell_sizes("width")
        self.icon2.rect = self.icon.rect
        self.icon.horz_align = "centre"
        self.icon2.horz_align = "centre"
        self.icon.vert_align = "bottom"
        self.icon2.vert_align = "bottom"
        if self.icon.font == "FontAwesome":
            self.icon.vert_align = "centre"

    def set_overlayed_symbol(self, icon, shape=None):
        if shape is not None:
            if shape.lower() == "circle":
                self.icon.font = "Zapf Dingbats"
                self.icon.text = "\u25CF"
            elif shape.lower() == "square":
                self.icon.font = "Zapf Dingbats"
                self.icon.text = "\u25A0"
            else:  # triangle
                self.icon.font = "Zapf Dingbats"
                self.icon.text = "\u25B2"
            set_icon(icon, self.icon2)
            self.icon.overlay_content = self.icon2
        else:
            self.icon.overlay_content = None
            set_icon(icon, self.icon)

    def set_safety_yellow(self):
        yellow = rl_colour_hex("#FFED10")
        self.icon.background_colour = (1, 1, 1)
        self.icon.font_colour = yellow
        self.icon2.background_colour = None
        self.icon2.font_colour = (0, 0, 0)
        sz = max(self.icon.font_size, self.icon2.font_size)
        self.icon.font = "Zapf Dingbats"
        self.icon2.font = "Hazard"
        self.icon.font_size = 0.9 * sz
        self.icon2.font_size = sz
        self.icon.overlay_content = self.icon2
        self.title.background_colour = yellow
        self.title.font_colour = (0, 0, 0)
        self.title.border_outline = True
        self.title.border_colour = (0, 0, 0)
        self._set_desc_rect()

    def _set_desc_rect(self):
        self.desc.background_colour = None
        self.desc.font_colour = (0, 0, 0)

    def _set_filled_title_rect(self, colour):
        self.icon.background_colour = None
        if self.icon.overlay_content is not None:
            self.icon.font_colour = (1, 1, 1)
            self.icon2.font_colour = colour
        else:
            self.icon.font_colour = colour
        self.title.background_colour = colour
        self.title.font_colour = (1, 1, 1)
        self.title.border_outline = False
        self._set_desc_rect()

    def set_safety_red(self):
        red = rl_colour_hex("#FB0207")
        self._set_filled_title_rect(red)

    def set_safety_blue(self):
        blue = rl_colour_hex("#0019BD")
        self._set_filled_title_rect(blue)

    def set_safety_green(self):
        green = rl_colour_hex("#148636")
        self._set_filled_title_rect(green)

    def set_debug_rects(self, show=False):
        self.title.show_debug_rects = show
        self.icon.show_debug_rects = show
        self.desc.show_debug_rects = show

    def draw_in_canvas(self, canvas, new_size=None):
        self.set_auto_size(canvas, new_size=new_size)
        super().draw_in_canvas(canvas)
