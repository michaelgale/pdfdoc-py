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
# PDF document utilities

import copy
from collections import OrderedDict
import string
from reportlab.lib.units import mm

from toolbox import Params
from pdfdoc import *

attr_aliases = {
    "title-color": "title-colour",
    "line-color": "line-colour",
    "font-color": "font-colour",
    "border-color": "border-colour",
    "background-color": "background-colour",
    "fill-color": "fill-colour",
    "horz-align": "horizontal-align",
    "vert-align": "vertical-align",
    "font": "font-name",
    "overlay-horz-align": "overlay-horizontal-align",
    "overlay-vert-align": "overlay-vertical-align",
    "columns": "ncolumns",
    "cols": "ncolumns",
    "rows": "nrows",
    "n-columns": "ncolumns",
    "n-rows": "nrows",
    "dash": "line-dash",
}


class DocStyle:
    """Container class for storing style information using CSS-like tag/attributes.
    This class offers the convenience of robust access to styles by name with features
    such default value substitution, aliases for attribute names (e.g. allowing the
    use of "colour" and "color"), and computation of derived values from the
    style such as page dimensions with or without margins/padding etc."""

    def __init__(self, style=None, **kwargs):
        self.__dict__["attr"] = {
            "length": 0,
            "width": 0,
            "height": 0,
            "orientation": "portrait",
            "left-margin": 0,
            "right-margin": 0,
            "top-margin": 0,
            "bottom-margin": 0,
            "alternating-margins": False,
            "ncolumns": 0,
            "nrows": 0,
            "top-padding": 0,
            "bottom-padding": 0,
            "left-padding": 0,
            "right-padding": 0,
            "padding-ratio": 0,
            "cell-padding": 0,
            "text-baseline": 0,
            "line-spacing": 1.1,
            "gutter-width": 0,
            "gutter-height": 0,
            "gutter-line": 0,
            "gutter-line-colour": (0, 0, 0),
            "title-width": 0,
            "title-height": 0,
            "title-font": "",
            "title-colour": (0, 0, 0),
            "title-font-size": 0,
            "font-name": DEF_FONT_NAME,
            "font-colour": (0, 0, 0),
            "font-alpha": 1,
            "font-size": DEF_FONT_SIZE,
            "line-width": 0.1 * mm,
            "line-colour": (0, 0, 0),
            "line-style": "solid",
            "line-dash": None,
            "border-width": 0,
            "border-colour": (0, 0, 0),
            "border-alpha": 1,
            "border-margin": 0,
            "background-colour": (0, 0, 0),
            "background-alpha": 1,
            "background-fill": False,
            "border-outline": False,
            "border-radius": 0.0,
            "vertical-align": "centre",
            "horizontal-align": "centre",
            "border-line-left": False,
            "border-line-right": False,
            "border-line-top": False,
            "border-line-bottom": False,
            "overlay-horizontal-align": "centre",
            "overlay-vertical-align": "centre",
            "overlay-size": "auto",
            "arrow-style": "taper",
            "arrow-auto-colour": True,
            "arrow-length": 0,
            "arrow-width": 0,
            "fill-colour": (0, 0, 0),
            "grid-colour": (0.5, 0.5, 0.5),
            "grid-line-width": 0,
            "grid-dash": [],
            "grid-interval": 0,
            "kerning": 0,
            "rotation": 0,
            "rotated-bounds": True,
        }
        if style is not None:
            self.set_with_dict(style)
        for k, v in kwargs.items():
            key = self._attr_key(k)
            self.set_attr(key, v)

    def __setitem__(self, key, value):
        self.set_attr(key, value)

    def __getitem__(self, key):
        return self.get_attr(key)

    def __getattr__(self, key):
        if key in self.attr:
            return self.attr[key]
        akey = self._attr_key(key)
        if akey in self.attr:
            return self.attr[akey]
        else:
            if key in dir(self):
                return getattr(self, key)
            return self.__dict__[key]

    def __setattr__(self, key, value):
        key = self._attr_key(key)
        if key in self.attr:
            self.set_attr(key, value)
        else:
            self.__dict__[key] = value

    def __repr__(self):
        return "%s()" % (self.__class__.__name__,)

    def _fmt_tuple(self, v):
        if any([isinstance(x, float) for x in v]):
            vs = ["%.3f, " % (x) for x in v]
            vs = "".join(vs)
            vs = vs.rstrip()
            vs = vs.rstrip(",")
            vs = "(%s)" % (vs)
            return vs
        return str(v)

    def __str__(self):
        s = []
        k1 = []
        v1 = []
        k2 = []
        v2 = []
        col = 0
        for key, value in self.attr.items():
            if not col:
                k1.append(key)
                v1.append(value)
            else:
                k2.append(key)
                v2.append(value)
            col = not col
        if len(v2) < len(v1):
            k2.append("")
            v2.append("")
        for key1, val1, key2, val2 in zip(k1, v1, k2, v2):
            if isinstance(val1, tuple):
                val1 = self._fmt_tuple(val1)
            if isinstance(val2, tuple):
                val2 = self._fmt_tuple(val2)
            s.append("%20s: %-16s %20s: %-16s" % (key1, val1, key2, val2))
        return "\n".join(s)

    def rgb_from_hex(self, hexStr):
        if len(hexStr) < 6:
            return 0, 0, 0
        hs = hexStr.lstrip("#")
        if not all(c in string.hexdigits for c in hs):
            return 0, 0, 0
        [rd, gd, bd] = tuple(int(hs[i : i + 2], 16) for i in (0, 2, 4))
        r = float(rd) / 255.0
        g = float(gd) / 255.0
        b = float(bd) / 255.0
        return r, g, b

    def _set_colour_attr(self, key, val):
        if "colour" in key or "color" in key:
            if isinstance(val, str):
                if val[0] == "#":
                    self.attr[key] = self.rgb_from_hex(val)
                    return True
        return False

    def add_attr(self, attr_name, attr_value=None):
        self.attr[attr_name] = attr_value

    def _attr_key(self, key):
        attr_name = key.replace("_", "-")
        attr_name = attr_name.lower()
        if attr_name in attr_aliases:
            alias = attr_aliases[attr_name]
            if alias in self.attr:
                return alias
        return attr_name

    def set_attr(self, attr_key, attr_value):
        key = self._attr_key(attr_key)
        if not self._set_colour_attr(key, attr_value):
            self.attr[key] = attr_value

    def get_attr(self, attr_key, def_value=None):
        key = self._attr_key(attr_key)
        if key in self.attr:
            return self.attr[key]
        return def_value

    def set_with_dict(self, style_dict, key_mask=None):
        if isinstance(style_dict, dict):
            items = style_dict.items()
        elif isinstance(style_dict, DocStyle):
            items = style_dict.attr.items()
        else:
            return
        if key_mask is not None:
            key_mask = [self._attr_key(k) for k in key_mask]
        for k, value in items:
            key = self._attr_key(k)
            if key_mask is not None and key not in key_mask:
                continue
            self.set_attr(key, value)
        # if DocStyle is passed with valid attribute names
        # not in attr, but in __dict__ then override with those
        if isinstance(style_dict, DocStyle):
            for k, v in style_dict.__dict__.items():
                if not k == "attr":
                    key = self._attr_key(k)
                    self.set_attr(key, v)

    def set_all_margins(self, withMargin):
        self.set_attr("left-margin", withMargin)
        self.set_attr("right-margin", withMargin)
        self.set_attr("top-margin", withMargin)
        self.set_attr("bottom-margin", withMargin)

    def set_top_margin(self, withMargin):
        self.set_attr("top-margin", withMargin)

    def set_bottom_margin(self, withMargin):
        self.set_attr("bottom-margin", withMargin)

    def set_right_margin(self, withMargin):
        self.set_attr("right-margin", withMargin)

    def set_left_margin(self, withMargin):
        self.set_attr("left-margin", withMargin)

    def set_lr_margins(self, withMargin):
        self.set_attr("left-margin", withMargin)
        self.set_attr("right-margin", withMargin)

    def set_tb_margins(self, withMargin):
        self.set_attr("top-margin", withMargin)
        self.set_attr("bottom-margin", withMargin)

    def set_all_padding(self, withPadding):
        self.set_attr("left-padding", withPadding)
        self.set_attr("right-padding", withPadding)
        self.set_attr("top-padding", withPadding)
        self.set_attr("bottom-padding", withPadding)

    def set_lr_padding(self, withPadding):
        self.set_attr("left-padding", withPadding)
        self.set_attr("right-padding", withPadding)

    def set_tb_padding(self, withPadding):
        self.set_attr("top-padding", withPadding)
        self.set_attr("bottom-padding", withPadding)

    def set_top_padding(self, withPadding):
        self.set_attr("top-padding", withPadding)

    def set_bottom_padding(self, withPadding):
        self.set_attr("bottom-padding", withPadding)

    def set_right_padding(self, withPadding):
        self.set_attr("right-padding", withPadding)

    def set_left_padding(self, withPadding):
        self.set_attr("left-padding", withPadding)

    # @property
    # def size(self):
    #     return self["width"], self["height"]

    @property
    def width_pad_margin(self):
        return self.get_width_trim()

    def get_width_trim(self):
        return (
            self.get_attr("left-margin", 0)
            + self.get_attr("right-margin", 0)
            + self.get_attr("left-padding", 0)
            + self.get_attr("right-padding", 0)
        )

    @property
    def height_pad_margin(self):
        return self.get_height_trim()

    def get_height_trim(self):
        return (
            self.get_attr("top-margin", 0)
            + self.get_attr("bottom-margin", 0)
            + self.get_attr("top-padding", 0)
            + self.get_attr("bottom-padding", 0)
        )

    @property
    def right_pad_margin(self):
        return self.get_right_trim()

    def get_right_trim(self):
        return self.get_attr("right-margin", 0) + self.get_attr("right-padding", 0)

    def get_right_margin(self):
        return self.get_attr("right-margin", 0)

    def get_right_padding(self):
        return self.get_attr("right-padding", 0)

    @property
    def left_pad_margin(self):
        return self.get_left_trim()

    def get_left_trim(self):
        return self.get_attr("left-margin", 0) + self.get_attr("left-padding", 0)

    def get_left_margin(self):
        return self.get_attr("left-margin", 0)

    def get_left_padding(self):
        return self.get_attr("left-padding", 0)

    @property
    def top_pad_margin(self):
        return self.get_top_trim()

    def get_top_trim(self):
        return self.get_attr("top-margin", 0) + self.get_attr("top-padding", 0)

    def get_top_margin(self):
        return self.get_attr("top-margin", 0)

    def get_top_padding(self):
        return self.get_attr("top-padding", 0)

    @property
    def bottom_pad_margin(self):
        return self.get_bottom_trim()

    def get_bottom_trim(self):
        return self.get_attr("bottom-margin", 0) + self.get_attr("bottom-padding", 0)

    def get_bottom_margin(self):
        return self.get_attr("bottom-margin", 0)

    def get_bottom_padding(self):
        return self.get_attr("bottom-padding", 0)

    def get_inset_rect(self, fromRect, odd_even_page_no=None):
        inset_rect = copy.copy(fromRect)
        if odd_even_page_no is not None and self.get_attr("alternating-margins", False):
            # odd page, swap left/right margin values
            # even page, use as is
            if int(odd_even_page_no) % 2 == 0:
                inset_rect.left += self.left_pad_margin
                inset_rect.right -= self.right_pad_margin
            else:
                inset_rect.left += self.right_pad_margin
                inset_rect.right -= self.left_pad_margin
        else:
            inset_rect.left += self.left_pad_margin
            inset_rect.right -= self.right_pad_margin
        inset_rect.top -= self.top_pad_margin
        inset_rect.bottom += self.bottom_pad_margin
        inset_rect.get_size()
        return inset_rect

    def get_margin_rect(self, fromRect=None, odd_even_page_no=None):
        if fromRect is not None:
            margin_rect = copy.copy(fromRect)
        else:
            margin_rect = Rect(self["width"], self["height"])
        if odd_even_page_no is not None and self["alternating-margins"]:
            # odd page, swap left/right margin values
            # even page, use as is
            if int(odd_even_page_no) % 2 == 0:
                margin_rect.left += self.left_margin
                margin_rect.right -= self.right_margin
            else:
                margin_rect.left += self.right_margin
                margin_rect.right -= self.left_margin
        else:
            margin_rect.left += self.left_margin
            margin_rect.right -= self.right_margin
        margin_rect.top -= self.top_margin
        margin_rect.bottom += self.bottom_margin
        margin_rect.get_size()
        return margin_rect

    @property
    def border_outline(self):
        return self["border-outline"]

    @border_outline.setter
    def border_outline(self, show=False):
        self.set_border_outline(show)

    def set_border_outline(self, show=False):
        if isinstance(show, str):
            if "top" in show.lower():
                self["border-line-top"] = True
            if "bottom" in show.lower():
                self["border-line-bottom"] = True
            if "left" in show.lower():
                self["border-line-left"] = True
            if "right" in show.lower():
                self["border-line-right"] = True
            if "all" in show.lower():
                self["border-outline"] = True
            if "none" in show.lower():
                self["border-outline"] = False
                self["border-line-top"] = False
                self["border-line-bottom"] = False
                self["border-line-left"] = False
                self["border-line-right"] = False
        else:
            self["border-outline"] = show

    @property
    def fill_colour_tuple(self):
        return tuple(int(x * 255) for x in self.fill_colour)

    @property
    def background_colour_tuple(self):
        return tuple(int(x * 255) for x in self.background_colour)

    @property
    def background_colour(self):
        return self["background-colour"]

    @background_colour.setter
    def background_colour(self, colour=None):
        if colour is None:
            self["background-fill"] = False
        else:
            self["background-fill"] = True
            self["background-colour"] = colour


class DocStyleSheet:
    """Container class for multiple DocStyle instances indexed in a dictionary.
    All the styles can be conveniently loaded from a YAML file.  The format of the
    YAML file must have a top level key called "styles" under which a tree of
    styles can be listed with the name of the style as a child of "styles" and the
    attributes of each style as children of the style name."""

    def __init__(self, filename=None):
        self.styles = {}
        if filename is not None:
            self.load_from_yml(filename)

    def __repr__(self):
        return "%s()" % (self.__class__.__name__,)

    def __getitem__(self, key):
        if key in self.styles:
            return self.styles[key]
        return None

    def __setitem__(self, key, value):
        self.set_style(key, value)

    def __iter__(self):
        for style in self.styles:
            yield style

    def print_styles(self):
        for k, v in self.styles.items():
            print(k)

    def clear(self):
        self.styles = {}

    def get_style(self, style_name):
        if style_name in self.styles:
            return self.styles[style_name]
        return None

    def set_style(self, style_name, style):
        if isinstance(style, dict):
            sd = DocStyle(style=style)
            self.styles[style_name] = sd
        elif isinstance(style, DocStyle):
            self.styles[style_name] = style

    def load_from_yml(self, filename):
        sp = Params(yml=filename, baseunit="pt")
        sd = sp.__dict__
        if "styles" in sd:
            for k, v in sd["styles"].items():
                s = DocStyle(style=v)
                self.styles[k] = s


def roman_number(num):
    roman = OrderedDict()
    roman[1000] = "M"
    roman[900] = "CM"
    roman[500] = "D"
    roman[400] = "CD"
    roman[100] = "C"
    roman[90] = "XC"
    roman[50] = "L"
    roman[40] = "XL"
    roman[10] = "X"
    roman[9] = "IX"
    roman[5] = "V"
    roman[4] = "IV"
    roman[1] = "I"

    def roman_num(num):
        for r in roman.keys():
            x, _ = divmod(num, r)
            yield roman[r] * x
            num -= r * x
            if num <= 0:
                break

    return "".join([a for a in roman_num(num)])


class DocStyleMixin:
    """Convenience class to add style semantics to another class."""

    def __getattr__(self, key):
        if "style" in self.__dict__:
            return self.style.get_attr(key)
        if key in dir(self):
            return getattr(self, key)
        return super().__getattr__(key)

    def __setattr__(self, key, value):
        if "style" in self.__dict__:
            self.style.set_attr(key, value)
        elif key in dir(self):
            setattr(self, key, value)
        super().__setattr__(key, value)
