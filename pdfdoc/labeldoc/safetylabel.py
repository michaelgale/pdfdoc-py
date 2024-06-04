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

from reportlab.pdfgen import canvas

from toolbox import *
from pdfdoc import *


class SafetyLabel(TableColumn):
    def __init__(
        self,
        icon,
        title,
        width=None,
        size=None,
        aspect_ratio=None,
        description=None,
        vertical=False,
        force_outlines=None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.vertical = vertical
        width = width if width is not None else 128 * mm
        if aspect_ratio is None:
            if self.vertical:
                aspect_ratio = 1.33
            else:
                aspect_ratio = 5
        ts = DocStyle(style=SAFETY_LABEL_TITLE, **kwargs)
        if size is not None:
            ts.font_size = size
            width, height = self.size_from_font_size(aspect_ratio, size)
            self.rect.set_size(width, height)
        else:
            height = width / aspect_ratio
            self.rect.set_size(width, width / aspect_ratio)
        bw = self.border_width_from_size(height)

        is_triangle = False
        if "icon_info" in icon:
            ic = SvgRect.from_preset("icon_info", **kwargs)
            ts.set_with_dict(SAFETY_INFO_STYLE)
        elif "mandatory" in icon:
            ic = SvgRect.from_preset(icon, **kwargs)
            ts.set_with_dict(SAFETY_BLUE_STYLE)
        elif "prohibited" in icon:
            ic = SvgRect.from_preset(icon, **kwargs)
            ts.set_with_dict(SAFETY_RED_STYLE)
        elif "icon_first_aid" in icon:
            ic = SvgRect.from_preset("icon_first_aid", **kwargs)
            ts.set_with_dict(SAFETY_GREEN_STYLE)
        elif "warning" in icon:
            ic = SvgRect.from_preset(icon, **kwargs)
            ts.set_with_dict(SAFETY_YELLOW_STYLE)
            is_triangle = True
        if force_outlines is not None:
            ts.border_outline = force_outlines

        if vertical:
            icon_width = width
            text_width = width
            if is_triangle:
                ic.set_fixed_size(width, width / 1.05)
            else:
                ic.set_fixed_size(width, width)
        else:
            icon_width = self.triangle_width_from_height(height)
            text_width = width - icon_width - 2 * bw
            ic.set_fixed_size(icon_width, height)

        self.set_title_box_style(ts, bw, is_triangle)
        ic.vert_align = "top"
        textbox = TableColumn(style=ts)
        title_style = DocStyle(ts)
        title_style.border_alpha = 0
        title_style.background_fill = False
        title_style.set_all_margins(0)
        title_style.set_tb_padding(2 * bw)
        desc_style = DocStyle(title_style)
        desc_style.font_size = ts.font_size * 0.70
        desc_style.horz_align = "centre"
        desc_style.set_all_margins(0)
        desc_style.set_all_padding(0)
        if vertical:
            desc_style.bottom_padding = 2 * bw
        desc_style.set_lr_padding(2 * bw)

        tr = TextRect(text_width, 1, title, style=title_style, split_lines=True)
        h = self.rect.height
        if tr.is_multi_line:
            tr.style.set_tb_padding(2 * bw)
        if description is None:
            if self.vertical:
                h = width + tr.get_content_size()[1]
                textbox.add_row("title", tr, height=CONTENT_SIZE)
            else:
                textbox.add_row("title", tr)

        if description is not None:
            h = 0 if not vertical else width
            h += tr.get_content_size()[1]
            desc = TextRect(
                text_width, 1, description, style=desc_style, split_lines=True
            )
            desc.vert_align = "top"
            h += desc.get_content_size()[1]
            if ts.border_width > 0:
                h += 2 * bw
            textbox.add_row("title", tr, height=CONTENT_SIZE)
            textbox.add_row("desc", desc, height=CONTENT_SIZE)

        self.rect.set_size(width, h)

        if not vertical:
            self.container = TableRow(width, h)
            self.container.add_column("icon", ic, width=CONTENT_SIZE)
            self.container.add_column("title", textbox)
        else:
            self.container = TableColumn(width, h)
            self.container.add_row("icon", ic, height=CONTENT_SIZE)
            self.container.add_row("title", textbox, height=CONTENT_SIZE)
        self.add_row("label", self.container)

    def border_width_from_size(self, size):
        if not self.vertical:
            return 0.07 * size
        return 0.02 * size

    def border_radius_from_height(self, height):
        return 0.125 * height

    def triangle_width_from_height(self, height):
        return 1.13 * height

    def size_from_font_size(self, aspect_ratio, font_size=None):
        sw = self.style.font_stroke(font_size)
        if not self.vertical:
            height = sw * (1 / (2 * self.border_width_from_size(1)))
            width = aspect_ratio * height
        else:
            width = 18 * sw
            height = aspect_ratio * width
        return width, height

    def set_title_box_style(self, title, bw, triangle):
        if not self.vertical:
            title.left_margin = 2 * bw
            if title.border_outline:
                title.border_width = bw
                title.right_margin = bw / 2
                title.left_margin = title.left_margin + bw / 2
                title.set_tb_margins(bw / 2)
            title.border_radius = self.border_radius_from_height(self.rect.height)
            if title.border_outline:
                title.border_radius -= bw / 2
        else:
            title.top_margin = 3 * bw if not triangle else bw
            if title.border_outline:
                title.border_width = bw
                title.top_margin = title.top_margin + bw / 2
            title.bottom_margin = bw / 2
            title.border_radius = self.border_radius_from_height(self.rect.width) / 2
            if title.border_outline:
                title.border_radius -= bw / 2
