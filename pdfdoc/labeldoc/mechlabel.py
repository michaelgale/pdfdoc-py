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
# Generic Label Class

import math

from reportlab.pdfgen import canvas

from toolbox import *
from pdfdoc import *
from pdfdoc.helpers import fraction_symbol

METRIC_SIZES = "M1.4 M1.5 M1.6 M2.5 M2 M3 M4 M5 M6 M8 M10".split()
IMPERIAL_SIZES = '#2 #4 #5 #6 #8 #10 #12 #1/4 #3/8 #5/16'.split()
HEAD_TYPES = "pan csk flat cheese socket hex carriage".split()
MECH_TYPES = ["star washer",
    "lock washer",
    "split washer",
    "washer", 
    "cage nut", 
    "lock nut", 
    "cap nut",
    "tee nut",
    "nut", 
    "bolt",
    "hook screw",
    "thumb screw",
    "grub screw",
    "wood screw",
    "machine screw",
    "screw",
    "standoff",
]
DRIVE_TYPES = "phillips torx robertson hex flat square pozi".split()
HAS_HEAD = ["bolt", "wood screw", "machine screw", "screw"]
HAS_DRIVE = ["bolt", "wood screw", "machine screw", "screw", "grub screw"]

SYMBOL_PREFIX_DICT = {
     "washer": "FlatWasher",
     "star washer": "StarWasher",
     "split washer": "SplitWasher",
     "lock washer": "SplitWasher",
     "lock nut": "LockNut",
     "cap nut": "CapNut",
     "tee nut": "TNut",
     "nut":  "HexNut",
     "hook screw": "Hook",
     "grub screw": "GrubScrew",
     "thumb screw": "ThumbScrew",
     "cage nut": "CageNut",
     "wood screw": "WS",
     "machine screw": "MS",
     "screw": "MS",
     "bolt": "Bolt",
}
DRIVE_SYMBOL_DICT = {
    "phillips": "Phillips",
    "torx": "Torx",
    "robertson": "Robertson",
    "hex": "Hex",
    "flat": "Flat",
    "square": "Robertson",
    "pozi": "Pozi",
}

TORX_SIZES = ["T%d" %(x+1) for x in range(30)]
PHILLIPS_SIZES = "PH0 PH1 PH2 PZ0 PZ1 PZ2 JIS #0 #00 #000".split()
ROBERTSON_SIZES = "#0 #1 #2 #3".split()


M15_COLOUR = "#54a9c8"
M16_COLOUR = "#3cb371"
M2_COLOUR = "#1498d7"
M25_COLOUR = "#00838f"
M3_COLOUR = "#237841"
M4_COLOUR = "#4c61db"
M5_COLOUR = "#81007b"
M6_COLOUR = "#3f3691"
M8_COLOUR = "#564e9d"
M10_COLOUR = "#a5a5cb"
MACHINE_SCREW_COLOUR = "#c91a09"
WOOD_SCREW_COLOUR = "#4b9f4a"
WOOD6_SCREW_COLOUR = "#237841"
WOOD8_SCREW_COLOUR = "#184632"

MCOLOUR_DICT = {
    "M1.5": M15_COLOUR,
    "M1.6": M16_COLOUR,
    "M2": M2_COLOUR,
    "M2.5": M25_COLOUR,
    "M3": M3_COLOUR,
    "M4": M4_COLOUR,
    "M5": M5_COLOUR,
    "M6": M6_COLOUR,
    "M8": M8_COLOUR,
    "M10": M10_COLOUR,
}

def trim_mech_title(text, level):
    if level == 1:
        text = text.replace(" Head,", ",")
    if level == 2:
        text = text.replace("Wood Screw", "Wood screw")
        text = text.replace("Machine Screw", "Machine screw")
        text = text.replace("Grub Screw", "Grub screw")
        text = text.replace("Thumb Screw", "Thumb screw")
    if level == 3:
        text = text.replace("Robertson", "Rob'son")
        text = text.replace("Machine screw", "Screw")
    if level == 4:
        text = text.replace("Phillips", "Ph")
        text = text.replace("Rob'son", "Square")
    return text

def trim_mech_title_callback(c, text, cr):
    return trim_string_function(c, text, cr.font, cr.font_size, cr.rect.width, trim_mech_title)

class MechanicalLabel(TableRow):
    def __init__(self, title="", subtitle=None, colour=None, symbol=None):
        super().__init__(0, 0)
        self.style.set_tb_padding(0.025 * inch)
        filename = symbol if symbol is not None else ""
        self.symbol = ImageRect(0, 0, filename=filename)
        self.symbol.style.set_lr_padding(0.03 * inch)
        self.symbol.vert_align = "top"
        self.textcol = TableColumn(0, 0)
        self.titlerow = TableRow(0, 0)
        self.title = TextRect(0, 0, title, GENERIC_LABEL_TITLE)
        self.title.style.set_attr("font-size", 12)
        self.title.style.set_attr("font-name", "IKEA-Sans-Heavy")
        self.title.style.set_attr("horz-align", "left")
        self.auxtitle = TextRect(0, 0, title, GENERIC_LABEL_TITLE)
        self.auxtitle.style.set_attr("font-size", 12)
        self.auxtitle.style.set_attr("font-name", "IKEA-Sans-Heavy")
        self.auxtitle.style.set_attr("horz-align", "left")
        if title[0] == "#" or title[0] == "`":
            titletext = title.split()[0]
            auxtext = title.split()[1:]
            auxtext = " ".join(auxtext)
            if title[0] == "`":
                self.title.text = titletext[1:]
            else:
                self.title.text = titletext
            self.auxtitle.text = auxtext
            if len(titletext) < 4:
                self.titlerow.add_column("Type", self.title, width=0.28)
            elif len(titletext) >= 8:
                self.titlerow.add_column("Type", self.title, width=0.6)
            elif len(titletext) > 5:
                self.titlerow.add_column("Type", self.title, width=0.48)
            else:
                self.titlerow.add_column("Type", self.title, width=0.42)

            self.titlerow.add_column("Aux", self.auxtitle, width=AUTO_SIZE)
            c = safe_colour_tuple(colour)
            self.title.style.set_attr("background-colour", c)
            self.title.style.set_attr("background-fill", True)
            self.title.style.set_attr("horz-align", "centre")
            self.title.style.set_attr("font-colour", high_contrast_complement(c))
        else:
            self.titlerow.add_column("Type", self.title, width=AUTO_SIZE)
        self.pattern = PatternRect(0, 0)
        self.pattern.pattern = ""
        if colour is not None:
            c = safe_colour_tuple(colour)
            self.pattern.style.set_attr("background-fill", True)
            self.pattern.style.set_attr("background-colour", c)
            self.pattern.foreground_colour = c
            self.pattern.background_colour = c
        self.subtitle = TextRect(0, 0, "", GENERIC_LABEL_DESC)
        self.subtitle.style.set_attr("font-size", 8)
        self.subtitle.style.set_attr("font-name", "DIN-Regular")
        self.subtitle.style.set_attr("horz-align", "left")
        
        if subtitle is not None:
            self.subtitle.text = subtitle
            self.subtitle.trim_callback = trim_mech_title_callback
        self.textcol.add_row("Title", self.titlerow, height=AUTO_SIZE)
        self.textcol.add_row("Pattern", self.pattern, height=0.07)
        self.textcol.add_row("SubTitle", self.subtitle, height=AUTO_SIZE)
        if symbol is not None:
            self.add_column("Symbol", self.symbol, width=0.22)
        self.add_column("Text", self.textcol, width=AUTO_SIZE)
        self.compute_cell_sizes("width")

    def set_debug_rects(self, show=False):
        self.title.show_debug_rects = show
        self.subtitle.show_debug_rects = show
        self.pattern.show_debug_rects = show
        self.symbol.show_debug_rects = show


class MechanicalItem:

    def __init__(self, **kwargs):
        self.type = None
        self.metric = False
        self.head = None
        self.drive = None
        self.drive_size = None
        self.size = 0
        self.length = 0
        self.units = None

    @property
    def has_head_type(self):
        if self.head is not None:
            return any(e == self.type for e in HAS_HEAD)
        return False
    
    @property
    def has_drive_type(self):
        return any(e == self.drive for e in HAS_DRIVE)
    
    @property
    def colour(self):
        if self.type == "wood screw":
            if self.size == "#6":
                return WOOD6_SCREW_COLOUR
            elif self.size == "#8":
                return WOOD8_SCREW_COLOUR
            return WOOD_SCREW_COLOUR
        if self.type == "machine screw" or self.type == "screw":
            if not self.metric:
                return MACHINE_SCREW_COLOUR
        if self.metric:
            return MCOLOUR_DICT[self.size]
        return "#808080"

    @property
    def head_description(self):
        if self.head is None:
            return ""
        if not self.has_head_type:
            return ""
        if "pan" in self.head:
            return "Pan Head"
        if "flat" in self.head or "csk" in self.head:
            return "CSK Head"
        if "socket" in self.head:
            return "Socket Head"
        if "hex" in self.head:
            return "Hex Head"
        if "cheese" in self.head:
            return "Cheese Head"
        if "carriage" in self.head:
            return "Carriage Head"
        return ""

    @property
    def description(self):
        s = []
        s.append(self.type.title())
        if self.has_head_type:
            s.append(self.head_description)
        if self.drive is not None:
            if self.drive_size is not None:
                s.append("%s %s" % (self.drive_size, self.drive.title()))
            else:
                s.append(self.drive.title())
        return ", ".join(s)
    
    @property
    def label_title(self):
        if self.length:
            ts = "`" + self.size + " × " + self.length
        else:
            ts = "`" + self.size
        if self.units:
            ts = ts + " " + self.units
        return ts
    
    @property
    def symbol_filename(self):
        s = []
        if self.type == "bolt" and self.drive is not None:
            s.append("MS")
        else:
            if self.type in SYMBOL_PREFIX_DICT:
                s.append(SYMBOL_PREFIX_DICT[self.type])
        if self.head is not None:
            hs = self.head
            hs = hs.replace("-head", "")
            hs = hs.replace("flat", "Flat")
            hs = hs.replace("csk", "Flat")
            s.append(hs.title())
        if self.drive is not None:
            if self.drive in DRIVE_SYMBOL_DICT:
                s.append(DRIVE_SYMBOL_DICT[self.drive])
        return "%s.png" % ("".join(s))

    @staticmethod
    def type_from_str(text):
        for e in ["star washer",
                "lock washer",
                "washer",
                "cap nut",
                "tee nut",
                "cage nut", 
                "lock nut", 
                "nut", 
                "bolt", 
                "hook screw",
                "grub screw",
                "wood screw",
                "machine screw",
                "thumb screw",
                "screw",
                "standoff",
            ]:
            if e in text.lower():
                return e
        size, _ = MechanicalItem.size_from_str(text)
        if size is not None:
            return "screw"
        return None
    
    @staticmethod
    def size_from_str(text):
        text = text.lstrip()
        size, metric = None, False
        ts = text.split()
        ts = ts[0].upper()
        for e in METRIC_SIZES:
            if ts.startswith(e):
                size = ts
                metric = True
                break
        if size is None:
            for e in IMPERIAL_SIZES:
                if ts.startswith(e):
                    size = ts
        return size, metric

    @staticmethod
    def length_from_str(text):
        len_flag = False
        len_str = None
        for e in text.split():
            if not len_flag and (e == "x" or e == "×"):
                len_flag = True
            elif len_flag:
                len_str = fraction_symbol(e)
                len_flag = False                
        return len_str
    
    @staticmethod
    def head_from_str(text):
        for e in HEAD_TYPES:
            if e in text.lower():
                return e
        return None

    @staticmethod
    def drive_from_str(text):
        for e in DRIVE_TYPES:
            if e in text.lower():
                return e
        return None

    @staticmethod
    def from_str(text):
        m = MechanicalItem()
        m.type = MechanicalItem.type_from_str(text)
        m.size, m.metric = MechanicalItem.size_from_str(text)
        m.length = MechanicalItem.length_from_str(text)
        if m.length is not None:
            if m.metric and "mm" in text:
                m.units = "mm"
                m.length = m.length.replace("mm", "")
        m.head = MechanicalItem.head_from_str(text)
        if m.type == "bolt":
            if m.head is None:
                m.head = "hex"
            if m.head == "flat":
                m.head = "hex"
        if m.has_head_type:
            if m.head is not None:
                ts = text.split()
                head_count = 0
                for t in ts:
                    if t.lower() == m.head:
                        head_count += 1
                if head_count >= 2:
                    th = text.lower().replace(m.head, "")
                    th = th + " " + m.head
                elif head_count == 1 and m.type == "bolt":
                    th = text.lower().replace(m.head, "")
                else:
                    th = text.lower()
                m.drive = MechanicalItem.drive_from_str(th)
            else:
                m.drive = MechanicalItem.drive_from_str(text)
            if m.drive == "torx":
                for e in TORX_SIZES:
                    if e in text:
                        m.drive_size = e
                        break
            elif m.drive == "phillips":
                for e in PHILLIPS_SIZES:
                    if e in text:
                        m.drive_size = e
                        break
            elif m.drive == "robertson":
                for e in ROBERTSON_SIZES:
                    if e in text:
                        m.drive_size = e
                        break
        return m
