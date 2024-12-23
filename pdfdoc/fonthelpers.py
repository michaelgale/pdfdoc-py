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
    "fa-caution": "\uF071",
    "mandatory": "\uF06A",
    "power-button": "\uF011",
    "paper": "\uF016",
    "paper-solid": "\uF15B",
    "home": "\uF015",
    "gear": "\uF013",
    "gears": "\uF085",
    "speaker-off": "\uF025",
    "speaker-min": "\uF026",
    "speaker-max": "\uF028",
    "label": "\uF02B",
    "labels": "\uF02C",
    "beaker": "\uF0C3",
    "wrench": "\uF0AD",
    "lightning": "\uF0E7",
    "apple": "\uF179",
    "windows": "\uF17A",
    "man": "\uF183",
    "woman": "\uF182",
    "box": "\uF1B2",
    "recycle": "\uF1B8",
    "plug": "\uF1E6",
    "wifi": "\uF1EB",
    "syringe": "\uF1FB",
    "puzzle": "\uF12E",
    "info": "\uF05A",
    "desktop-pc": "\uF108",
    "laptop-pc": "\uF109",
    "tablet": "\uF10A",
    "phone": "\uF10B",
    "cup": "\uF0F4",
    "lightbulb": "\uF0EB",
    "truck": "\uF0D1",
    "list": "\uF0CA",
    "paperclip": "\uF0C6",
    "people": "\uF0C0",
    "link": "\uF0C1",
    "toolbox": "\uF0B1",
    "globe": "\uF0AC",
    "bell": "\uF0A2",
    "horn": "\uF0A1",
    "unlock": "\uF09C",
    "cart": "\uF07A",
    "magnet": "\uF076",
    "calendar": "\uF073",
    "airplane": "\uF072",
    "gift": "\uF06B",
    "fa-prohibited": "\uF05E",
    "question": "\uF059",
    "crosshair": "\uF05B",
    "check-yes": "\uF058",
    "cross-no": "\uF057",
    "nav-first": "\uF048",
    "nav-prev": "\uF049",
    "nav-rew": "\uF04A",
    "nav-play": "\uF04B",
    "nav-pause": "\uF04C",
    "nav-stop": "\uF04D",
    "nav-fwd": "\uF04E",
    "nav-next": "\uF050",
    "nav-last": "\uF051",
    "nav-eject": "\uF052",
    "pencil": "\uF040",
    "camera": "\uF030",
    "lock": "\uF023",
    "trash": "\uF014",
    "person": "\uF007",
    "star": "\uF005",
    "envelope": "\uF003",
    "find": "\uF002",
    "music": "\uF001",
    "x": "\uF00D",
    "check": "\uF00C",
    "flag": "\uF024",
    "water": "\uF043",
    "leaf": "\uF06C",
    "up-down": "\uF07D",
    "left-right": "\uF07E",
    "boxes": "\uF1B3",
    "shower": "\uF2CC",
    "chip": "\uF2DB",
    "snowflake": "\uF2DC",
    "thermometer": "\uF2C9",
    "bluetooth": "\uF294",
    "bluetooth-solid": "\uF293",
    "batt-full": "\uF240",
    "batt-3quarter": "\uF241",
    "batt-half": "\uF242",
    "batt-quarter": "\uF243",
    "batt-empty": "\uF244",
    "train-headlight": "\uF238",
    "train-twolight": "\uF239",
    "brush": "\uF1FC",
    "truck": "\uF0D1",
    "receipt": "\uF298",
    "orders": "\uF218",
    "inbox": "\uF01C",
    "round-left": "\uF0A8",
    "round-right": "\uF0A9",
    "round-up": "\uF0AA",
    "round-down": "\uF0AB",
    "yes-box": "\uF14A",
    "thumb-up": "\uF164",
    "thumb-down": "\uF165",
    "wheelchair": "\uF193",
    "file-pdf": "\uF1C1",
    "file-image": "\uF1C5",
    "file-audio": "\uF1C7",
    "file-video": "\uF1C8",
    "file-code": "\uF1C9",
    "hourglass": "\uF253",
    "usb": "\uF287",
    "first-aid-box": "\uF0FA",
    "speed": "\uF0E4",
    "pushpin": "\uF08D",
    "calendar": "\uF073",
    "repeat": "\uF021",
    "house": "\uF015",
    "search": "\uF002",
    "tag": "\uF02B",
    "tags": "\uF02C",
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
    "exit": "\u005E",
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

    @property
    def stroke_width(self):
        c = canvas.Canvas("tmp.pdf")
        width = c.stringWidth("i", self.font_name, self.font_size)
        return width

    def string_width(self, s):
        c = canvas.Canvas("tmp.pdf")
        c.setFont(self.font_name, self.font_size)
        tw = c.stringWidth(s, self.font_name, self.font_size)
        return tw
