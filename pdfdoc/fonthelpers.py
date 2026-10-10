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

import os, os.path

from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont

from toolbox import full_path, split_path, split_filename, Point
from pdfdoc import FONT_PATHS, REGISTERED_FONTS


def _clean_name(name):
    return name.replace(" ", "").replace("-", "").replace("_", "")


def get_system_font_list(spec="*"):
    font_list = []
    for font_path in FONT_PATHS:
        dirname = full_path(font_path)
        if os.path.isdir(dirname):
            files = Path(dirname).rglob(spec)
            for f in list(files):
                if not os.path.isdir(f):
                    fn = str(f).lower()
                    if fn.endswith("ttf") or fn.endswith("ttc"):
                        font_list.append(str(f))
    return font_list


def print_system_fonts(spec="*"):
    import crayons

    fonts = sorted(get_system_font_list("*.ttf"))
    print("TrueType Fonts")
    for i, font in enumerate(fonts):
        _, fn = split_path(font)
        print("%3d." % (i + 1), crayons.cyan(str(fn), bold=True))
    fonts = sorted(get_system_font_list("*.ttc"))
    print("TrueType Fonts Families")
    for i, font in enumerate(fonts):
        _, fn = split_path(font)
        print("%3d." % (i + 1), crayons.blue(str(fn), bold=True))


def find_font(font):
    font = _clean_name(font)
    font_list = get_system_font_list("*")
    for f in font_list:
        _, fn = split_path(f)
        fp, fext = split_filename(fn)
        fname = _clean_name(fp)
        if fname.lower() == font.lower() and not fext.lower().endswith("otf"):
            name = fp.replace(" ", "-")
            return name, f
        elif font.lower().endswith(".ttc") or font.lower().endswith(".ttf"):
            fe = font.lower().replace(".ttc", "").replace(".ttf", "")
            if fname.lower() == fe:
                name = fp.replace(" ", "-")
                return name, f
    return None, None


def register_font_family(font_path):
    if not os.path.isfile(full_path(font_path)):
        fname, ffile = find_font(font_path)
        if fname is None or ffile is None:
            print("Font family %s cannot be found" % (font_path))
            return None
        font_path = ffile
    _, fn = split_path(font_path)
    ff, _ = split_filename(fn)
    fname = ff.replace(" ", "-")
    valid_subfonts = []
    for i in range(20):
        fontname = "%s-%d" % (fname, i)
        try:
            pdfmetrics.registerFont(TTFont(fontname, font_path, subfontIndex=i))
            valid_subfonts.append(fontname)
        except:
            pass
    return valid_subfonts


def register_font(font_name, font_filename=None):
    if font_name in REGISTERED_FONTS:
        return font_name, font_filename
    if font_filename is not None:
        try:
            pdfmetrics.registerFont(TTFont(font_name, font_filename))
            return font_name, font_filename
        except:
            pass
    fname, ffile = find_font(font_name)
    if fname is not None:
        try:
            pdfmetrics.registerFont(TTFont(fname, ffile))
            return fname, ffile
        except:
            print("Unable to register font %s (%s)" % (fname, ffile))
    return None, None


def get_registered_fonts():
    return REGISTERED_FONTS


def create_specimen_pdf(font, filename, size=28):
    from pdfdoc.contentrect.textrect import TextRect

    fname, _ = register_font(font)
    _font_dict = {
        "font-name": fname,
        "font-size": 18,
        "horz-align": "left",
    }
    c = canvas.Canvas(filename, pagesize=(8.5 * inch, 11.0 * inch))
    c.saveState()
    t1 = TextRect(7 * inch, 0.5 * inch, "Font Specimen: %s" % (fname), style=_font_dict)
    t1.top_left = Point(1 * inch, 10 * inch)
    t1.draw_in_canvas(c)
    _font_dict = {
        "font-name": fname,
        "font-size": size,
        "horz-align": "centre",
    }
    char_list = [
        "0 1 2 3 4 5 6 7 8 9 _",
        "! @ # $ % & * ( ) { }",
        ": ; < > , . ? / ~ [ ]",
        "= + - £ € µ ¥ © ® ß ™",
        "A B C D E F G H I J K",
        "L M N O P Q R S T U V",
        "W X Y Z a b c d e f g",
        "h i j k l m n o p q r",
        "s t u v w x y z",
    ]
    for i, line in enumerate(char_list):
        for j, ch in enumerate(line):
            t1 = TextRect(0.65 * inch, 0.5 * inch, ch, style=_font_dict)
            pt = 1 * inch + j * 0.3 * inch, 9.5 * inch - i * 0.75 * inch
            t1.top_left = Point(*pt)
            t1.draw_in_canvas(c)
    c.showPage()
    c.save()


def create_font_family_pdf(fontname, pdffile):
    from pdfdoc.contentrect.textrect import TextRect

    _font_dict = {
        "font-name": "Avenir-0",
        "font-size": 18,
        "horz-align": "left",
    }
    valid_fonts = register_font_family(fontname)
    c = canvas.Canvas(pdffile, pagesize=(8.5 * inch, 11.0 * inch))
    c.saveState()
    for i, font in enumerate(valid_fonts):
        _font_dict["font-name"] = font
        t1 = TextRect(
            7 * inch, 0.5 * inch, "%s Font Specimen" % (font), style=_font_dict
        )
        t1.top_left = Point(1 * inch, 10 * inch - i * 0.5 * inch)
        t1.draw_in_canvas(c)
    c.showPage()
    c.save()


fa_lookup_dict = {
    "fa-caution": "\uf071",
    "mandatory": "\uf06a",
    "power-button": "\uf011",
    "paper": "\uf016",
    "paper-solid": "\uf15b",
    "home": "\uf015",
    "gear": "\uf013",
    "gears": "\uf085",
    "speaker-off": "\uf025",
    "speaker-min": "\uf026",
    "speaker-max": "\uf028",
    "label": "\uf02b",
    "labels": "\uf02c",
    "beaker": "\uf0c3",
    "wrench": "\uf0ad",
    "lightning": "\uf0e7",
    "apple": "\uf179",
    "windows": "\uf17a",
    "man": "\uf183",
    "woman": "\uf182",
    "box": "\uf1b2",
    "recycle": "\uf1b8",
    "plug": "\uf1e6",
    "wifi": "\uf1eb",
    "syringe": "\uf1fb",
    "puzzle": "\uf12e",
    "info": "\uf05a",
    "desktop-pc": "\uf108",
    "laptop-pc": "\uf109",
    "tablet": "\uf10a",
    "phone": "\uf10b",
    "cup": "\uf0f4",
    "lightbulb": "\uf0eb",
    "truck": "\uf0d1",
    "list": "\uf0ca",
    "paperclip": "\uf0c6",
    "people": "\uf0c0",
    "link": "\uf0c1",
    "toolbox": "\uf0b1",
    "globe": "\uf0ac",
    "bell": "\uf0a2",
    "horn": "\uf0a1",
    "unlock": "\uf09c",
    "cart": "\uf07a",
    "magnet": "\uf076",
    "calendar": "\uf073",
    "airplane": "\uf072",
    "gift": "\uf06b",
    "fa-prohibited": "\uf05e",
    "question": "\uf059",
    "crosshair": "\uf05b",
    "check-yes": "\uf058",
    "cross-no": "\uf057",
    "nav-first": "\uf048",
    "nav-prev": "\uf049",
    "nav-rew": "\uf04a",
    "nav-play": "\uf04b",
    "nav-pause": "\uf04c",
    "nav-stop": "\uf04d",
    "nav-fwd": "\uf04e",
    "nav-next": "\uf050",
    "nav-last": "\uf051",
    "nav-eject": "\uf052",
    "pencil": "\uf040",
    "camera": "\uf030",
    "lock": "\uf023",
    "trash": "\uf014",
    "person": "\uf007",
    "star": "\uf005",
    "envelope": "\uf003",
    "find": "\uf002",
    "music": "\uf001",
    "x": "\uf00d",
    "check": "\uf00c",
    "flag": "\uf024",
    "water": "\uf043",
    "leaf": "\uf06c",
    "up-down": "\uf07d",
    "left-right": "\uf07e",
    "boxes": "\uf1b3",
    "shower": "\uf2cc",
    "chip": "\uf2db",
    "snowflake": "\uf2dc",
    "thermometer": "\uf2c9",
    "bluetooth": "\uf294",
    "bluetooth-solid": "\uf293",
    "batt-full": "\uf240",
    "batt-3quarter": "\uf241",
    "batt-half": "\uf242",
    "batt-quarter": "\uf243",
    "batt-empty": "\uf244",
    "train-headlight": "\uf238",
    "train-twolight": "\uf239",
    "brush": "\uf1fc",
    "truck": "\uf0d1",
    "receipt": "\uf298",
    "orders": "\uf218",
    "inbox": "\uf01c",
    "round-left": "\uf0a8",
    "round-right": "\uf0a9",
    "round-up": "\uf0aa",
    "round-down": "\uf0ab",
    "yes-box": "\uf14a",
    "thumb-up": "\uf164",
    "thumb-down": "\uf165",
    "wheelchair": "\uf193",
    "file-pdf": "\uf1c1",
    "file-image": "\uf1c5",
    "file-audio": "\uf1c7",
    "file-video": "\uf1c8",
    "file-code": "\uf1c9",
    "hourglass": "\uf253",
    "usb": "\uf287",
    "first-aid-box": "\uf0fa",
    "speed": "\uf0e4",
    "pushpin": "\uf08d",
    "calendar": "\uf073",
    "repeat": "\uf021",
    "house": "\uf015",
    "search": "\uf002",
    "tag": "\uf02b",
    "tags": "\uf02c",
}


def fa_symbol(x):
    """Returns a FontAwesome symbol using a descriptive name"""
    if x.lower() in fa_lookup_dict:
        return fa_lookup_dict[x.lower()]
    return ""


haz_lookup_dict = {
    "caution": "!",
    "laser": "C",
    "radiation": "E",
    "electrical": "F",
    "fire": "H",
    "poison": "I",
    "oxidization": "L",
    "eye-protection": "l",
    "boots": "m",
    "gloves": "n",
    "hat": "o",
    "ear-protection": "p",
    "wash-hands": "w",
    "face-shield": "x",
    "face-mask": "y",
    "no-people": "b",
    "no-smoking": "d",
    "no-cups": "f",
    "no-utensils": "g",
    "no-food": "=",
    "exit": "\u005e",
    "first-aid": "Q",
    "left-arrow": "R",
    "right-arrow": "S",
    "up-arrow": "T",
    "down-arrow": "U",
    "prohibited": "1",
    "power-off": "u",
}

haz_shape_dict = {
    "caution": "triangle",
    "laser": "triangle",
    "radiation": "triangle",
    "electrical": "triangle",
    "fire": "triangle",
    "poison": "triangle",
    "oxidization": "triangle",
    "eye-protection": "circle",
    "boots": "circle",
    "gloves": "circle",
    "hat": "circle",
    "ear-protection": "circle",
    "wash-hands": "circle",
    "face-shield": "circle",
    "face-mask": "circle",
    "no-people": "circle",
    "no-smoking": "circle",
    "no-cups": "circle",
    "no-utensils": "circle",
    "no-food": "circle",
    "exit": "square",
    "first-aid": "square",
    "left-arrow": "square",
    "right-arrow": "square",
    "up-arrow": "square",
    "down-arrow": "square",
    "prohibited": "circle",
    "power-off": "circle",
    "fa-caution": "triangle",
    "mandatory": "circle",
    "fa-info": "circle",
    "info": "circle",
}


def haz_symbol(x):
    """Returns a Hazard symbol using a descriptive name"""
    if x.lower() in haz_lookup_dict:
        return haz_lookup_dict[x.lower()]
    return ""


def set_icon(x, textrect):
    """Automatically fills a TextRect with an icon from Hazard or FontAwesome fonts"""
    sx = haz_symbol(x)
    if len(sx):
        textrect.style["font-name"] = "Hazard"
        textrect.text = sx
    else:
        textrect.style["font-name"] = "FontAwesome"
        textrect.text = fa_symbol(x)


def print_symbol_list():
    s = []
    idx = 0
    for k, v in haz_lookup_dict.items():
        s.append("%-20s" % (k))
        idx += 1
        if idx % 4 == 0:
            print("".join(s))
            s = []
    for k, v in fa_lookup_dict.items():
        s.append("%-20s" % (k))
        idx += 1
        if idx % 4 == 0:
            print("".join(s))
            s = []
    print("".join(s))


class FontWrapper:
    def __init__(self, font_name, font_size, **kwargs):
        self.font_name = font_name
        self.font_size = font_size
        self._face = None

    @property
    def face(self):
        if self._face is None:
            self._face = pdfmetrics.getFont(self.font_name).face
        return self._face

    @property
    def ascent(self):
        return self.face.ascent / 1000.0 * self.font_size

    @property
    def descent(self):
        return self.face.descent / 1000.0 * self.font_size

    @property
    def nom_height(self):
        return self.ascent - self.descent

    @property
    def height(self):
        if abs(self.ascent - self.font_size) / self.font_size < 0.1:
            return self.ascent
        return self.ascent - self.descent

    def stroke_width(self, size=None):
        c = canvas.Canvas("tmp.pdf")
        size = size if size is not None else self.font_size
        width = c.stringWidth("i", self.font_name, size)
        return width

    def string_width(self, s, size=None):
        c = canvas.Canvas("tmp.pdf")
        size = size if size is not None else self.font_size
        c.setFont(self.font_name, size)
        tw = c.stringWidth(s, self.font_name, size)
        return tw
