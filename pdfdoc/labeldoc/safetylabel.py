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
from pdfdoc.fonthelpers import haz_shape_dict, stroke_width


class SafetyLabel(TableRow):
    def __init__(
        self,
        icon,
        title,
        width=None,
        size=None,
        aspect_ratio=None,
        description=None,
        **kwargs
    ):
        super().__init__(**kwargs)
        width = width if width is not None else 128 * mm
        aspect_ratio = aspect_ratio if aspect_ratio is not None else 5
        ts = DocStyle(style=SAFETY_LABEL_TITLE, **kwargs)
        if size is not None:
            ts.font_size = size
            h = self.height_from_font_size(ts.font_name, size)
            width = aspect_ratio * h
        self.rect.set_size(width, width / aspect_ratio)
        bw = self.border_width_from_height(self.rect.height)
        ts.left_margin = 2 * bw
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
        if ts.border_outline:
            ts.border_width = bw
            ts.right_margin = bw / 2
            ts.left_margin = ts.left_margin + bw / 2
            ts.set_tb_margins(bw / 2)
        ts.border_radius = self.border_radius_from_height(self.rect.height)
        if ts.border_outline:
            ts.border_radius -= bw / 2
        ic.set_fixed_size(
            self.triangle_width_from_height(self.rect.height), self.rect.height
        )
        ic.vert_align = "top"
        textbox = TableColumn(style=ts)
        title_style = DocStyle(ts)
        title_style.border_alpha = 0
        title_style.background_fill = False
        title_style.set_all_margins(0)
        title_style.set_all_padding(0)
        desc_style = DocStyle(title_style)
        desc_style.font_size = title_style.font_size * 0.7
        desc_style.horz_align = "left"
        desc_style.set_lr_padding(3 * bw)
        desc_style.top_padding = bw
        tr = TextRect(title, style=title_style, split_lines=False)
        if description is None:
            textbox.add_row("title", tr)
        h = self.rect.height
        if description is not None:
            textbox.add_row("title", tr, height=CONTENT_SIZE)
            desc = TextRect(description, style=desc_style)
            textbox.add_row("desc", desc, height=CONTENT_SIZE)
            h += desc.get_content_size()[1]
            h += 2 * bw
            if ts.border_width > 0:
                h += 2 * bw
        self.add_column("icon", ic, width=CONTENT_SIZE)
        self.add_column("title", textbox)
        self.rect.set_size(width, h)

    def border_width_from_height(self, height):
        return 0.07 * height

    def border_radius_from_height(self, height):
        return 0.125 * height

    def triangle_width_from_height(self, height):
        return 1.13 * height

    def height_from_font_size(self, font, font_size=None):
        if isinstance(font, DocStyle):
            fn = font["font-name"]
            fs = font["font-size"]
        else:
            fn, fs = font, font_size
        sw = stroke_width(fn, fs)
        height = sw * (1 / (2 * self.border_width_from_height(1)))
        return height
