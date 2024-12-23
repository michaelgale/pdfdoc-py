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
# Utility DocumentCallback classes

from toolbox import *
from pdfdoc import *


class DocumentCallback:
    """A generic base class which implements behaviour for Document class
    callback actions at intervals such as page breaks, sections and document start/end.
    """

    def __init__(self):
        self.page_exclusions = []
        self.section_exclusions = []
        self.pages_active = None
        self.sections_active = None
        self.z_order = 0

    def __repr__(self):
        return "%s()" % (self.__class__.__name__,)

    def is_enabled(self, context):
        """A callback action can be masked or triggered by exclusions/permissions
        to confine its action to specific pages and/or sections of a document."""
        if context["page_number"] in self.page_exclusions:
            return False
        if context["section"] in self.section_exclusions:
            return False
        if self.sections_active is not None:
            if not context["section"] in self.sections_active:
                return False
        if self.pages_active is not None:
            if not context["page_number"] in self.pages_active:
                return False

        return True

    def render(self, context):
        """Implemented by instances of this class. The context stores a dictionary
        containing context information for the document such as the current page,
        page coordinate, etc."""
        pass


class SimpleHeaderFooterCallback(DocumentCallback):
    """A simple header and/or footer callback for generic content. The content is
    a ContentRect type and implements the draw_in_canvas method."""

    def __init__(
        self,
        content=None,
        show_in_footer=False,
        show_in_header=False,
        show_odd=True,
        show_even=True,
    ):
        super().__init__()
        self.content = content
        self.show_odd = show_odd
        self.show_even = show_even
        self.show_in_footer = show_in_footer
        self.show_in_header = show_in_header

    def _show_content(self, context):
        page_num = context["page_number"]
        even_page = int(page_num) % 2 == 0
        if self.show_odd and not even_page:
            self.content.draw_in_canvas(context["canvas"])
        if self.show_even and even_page:
            self.content.draw_in_canvas(context["canvas"])

    def render(self, context):
        if self.show_in_footer:
            self.content.rect = context["footer_rect"]
            self._show_content(context)
        if self.show_in_header:
            self.content.rect = context["header_rect"]
            self._show_content(context)


class PageNumberCallback(SimpleHeaderFooterCallback):
    """A flexible and simple page numbering callback."""

    def __init__(
        self,
        show_in_footer=False,
        show_in_header=False,
        alternate_odd_even=False,
        number_format="arabic",
        style=None,
    ):
        super().__init__()
        self.alternate_odd_even = alternate_odd_even
        self.show_in_footer = show_in_footer
        self.show_in_header = show_in_header
        self.content = TextRect(0, 0, "", style=style)
        self.number_format = number_format

    def set_style(self, with_style):
        self.content.style.set_with_dict(with_style)

    def render(self, context):
        if self.alternate_odd_even:
            if int(context["page_number"]) % 2 == 0:
                self.content.style["horz-align"] = "left"
            else:
                self.content.style["horz-align"] = "right"
        if self.number_format.lower() == "roman":
            num_text = roman_number(context["page_number"])
        elif self.number_format.lower() == "roman-lowercase":
            num_text = roman_number(context["page_number"])
            num_text = num_text.lower()
        else:
            num_text = str(context["page_number"])
        self.content.text = num_text
        super().render(context)


class PageBackgroundCallback(DocumentCallback):
    """Simple solid coloured page background callback."""

    def __init__(self, colour=None, style=None, draw_in_bleed=None):
        super().__init__()
        self.colour = colour if colour is not None else (1, 1, 1)
        self.style = DocStyle()
        self.style.set_with_dict(style)
        if style is None:
            style = {"background-fill": True, "background-colour": self.colour}
        self.background = ContentRect(0, 0, style=style)
        self.z_order = -1
        if draw_in_bleed is not None:
            self.draw_in_bleed = draw_in_bleed
        else:
            self.draw_in_bleed = False

    def render(self, context):
        if self.draw_in_bleed:
            self.background.rect = context["bleed_rect"]
        else:
            self.background.rect = context["page_rect"]
        self.background.draw_in_canvas(context["canvas"])


class CropMarksCallback(DocumentCallback):
    """A callback which draws crop marks in the bleed area of the page."""

    def __init__(self, length, style=None):
        super().__init__()
        self.length = length
        self.style = DocStyle(style=style)
        self.show_cross_hairs = False
        self.show_as_corners = True

    def _draw_cross(self, context, centre_pt):
        c = context["canvas"]
        x = centre_pt[0]
        y = centre_pt[1]
        l2 = self.length / 2
        c.line(x - l2, y, x + l2, y)
        c.line(x, y - l2, x, y + l2)

    def render(self, context):
        r = context["page_rect"]
        c = context["canvas"]
        l = self.length
        line_colour = self.style.get_attr("line-colour", (0, 0, 0))
        line_width = self.style.get_attr("line-width", MM2PTS(0.1))
        c.setStrokeColor(rl_colour(line_colour))
        c.setLineWidth(line_width)

        if self.show_as_corners:
            # top left
            c.line(r.left - l, r.top, r.left, r.top)
            c.line(r.left, r.top, r.left, r.top + l)
            # top right
            c.line(r.right, r.top, r.right, r.top + l)
            c.line(r.right, r.top, r.right + l, r.top)
            # bottom left
            c.line(r.left - l, r.bottom, r.left, r.bottom)
            c.line(r.left, r.bottom, r.left, r.bottom - l)
            # bottom right
            c.line(r.right, r.bottom, r.right, r.bottom - l)
            c.line(r.right, r.bottom, r.right + l, r.bottom)
        if self.show_cross_hairs:
            pts = r.get_pts()
            for pt in pts:
                self._draw_cross(context, pt)


class FoldMarkCallback(DocumentCallback):
    """A callback which draws fold marks in the bleed area of the page."""

    def __init__(self, length, style=None):
        super().__init__()
        self.length = length
        self.style = DocStyle(style=style)
        self.line_dash = [1.5, 3, 1.5, 0]
        self.orientation = "vertical"

    def render(self, context):
        r = context["page_rect"]
        c = context["canvas"]
        l = self.length
        line_colour = self.style.get_attr("line-colour", (0, 0, 0))
        line_width = self.style.get_attr("line-width", MM2PTS(0.1))
        c.setStrokeColor(rl_colour(line_colour))
        c.setLineWidth(line_width)
        c.setDash(array=self.line_dash)
        if self.orientation.lower() == "vertical":
            mid = r.left + (r.right - r.left) / 2.0
            c.line(mid, r.top, mid, r.top + l)
            c.line(mid, r.bottom, mid, r.bottom - l)
        else:
            mid = r.bottom + (r.top - r.bottom) / 2.0
            c.line(r.left, mid, r.left - l, mid)
            c.line(r.right, mid, r.right + l, mid)
        c.setDash([])


class ColumnLineCallback(DocumentCallback):
    """A callback which draws column dividing line in the gutter."""

    def __init__(self, style=None):
        super().__init__()
        self.style = DocStyle(style=style)

    def render(self, context):
        if context["gutter_rect"] is None:
            return
        r = context["gutter_rect"]
        c = context["canvas"]
        line_colour = self.style.get_attr("line-colour", (0, 0, 0))
        line_width = self.style.get_attr("line-width", 0.5 * mm)
        tm = self.style.top_pad_margin
        bm = self.style.bottom_pad_margin
        c.setStrokeColor(rl_colour(line_colour))
        c.setLineWidth(line_width)
        x = r.left + r.width / 2
        c.line(x, r.top - tm, x, r.bottom + bm)


class WatermarkCallback(DocumentCallback):
    """A callback which draws watermark text on top of the page."""

    default_style = {
        "font": "DIN-Bold",
        "font-size": 64,
        "font-colour": "#601010",
        "kerning": 0.4,
        "font-alpha": 0.25,
        "rotation": 22,
    }

    def __init__(self, text=None, style=None):
        super().__init__()
        self.text = text
        self.style = DocStyle(style=style)
        self.z_order = 99
        if style is None:
            self.style.set_with_dict(self.default_style)

    def render(self, context):
        if self.text is None:
            return
        tr = TextRect(self.text, style=self.style)
        tr.rect.move_to(context["page_rect"].centre)
        tr.draw_in_canvas(context["canvas"])
