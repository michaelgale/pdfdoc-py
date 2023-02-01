#! /usr/bin/env python3
#
# Copyright (C) 2023  Michael Gale

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
# CMYKGrid class derived from TableColumn

from toolbox import *
from pdfdoc import *


class CMYKGrid(TableColumn):
    """Draws a grid of CMYK colours over a range of channel values
    Useful for colour calibration of printers."""

    def __init__(self, w=None, h=None, **kwargs):
        self.rows = 8
        self.cols = 8
        self.top_left_cmyk = (0, 0, 0, 0)
        self.row_channel = "Y"
        self.col_channel = "M"
        self.row_inc = 0.02
        self.col_inc = 0.02
        self.labels = True
        self.labels_in_pct = True
        self.label_style = DocStyle()
        self.padding = 0
        for k, v in kwargs.items():
            if k in self.__dict__:
                self.__dict__[k] = v
        if w is None:
            w = MM2PTS(72)
        if h is None:
            h = MM2PTS(72)
        super().__init__(w, h)

    def __repr__(self):
        return "%s()" % (self.__class__.__name__,)

    def inc_channel(self, cmyk, channel, inc):
        if channel.upper() == "C":
            v = (cmyk[0] + inc, cmyk[1], cmyk[2], cmyk[3])
        elif channel.upper() == "M":
            v = (cmyk[0], cmyk[1] + inc, cmyk[2], cmyk[3])
        elif channel.upper() == "Y":
            v = (cmyk[0], cmyk[1], cmyk[2] + inc, cmyk[3])
        elif channel.upper() == "K":
            v = (cmyk[0], cmyk[1], cmyk[2], cmyk[3] + inc)
        return clamp_cmyk(v)

    def get_cmyk_channel(self, cmyk, channel):
        if channel.upper() == "C":
            return cmyk[0]
        elif channel.upper() == "M":
            return cmyk[1]
        elif channel.upper() == "Y":
            return cmyk[2]
        return cmyk[3]

    def set_cmyk_channel(self, cmyk, v, channel):
        new_cmyk = list(cmyk)
        if channel.upper() == "C":
            new_cmyk[0] = v
        elif channel.upper() == "M":
            new_cmyk[1] = v
        elif channel.upper() == "Y":
            new_cmyk[2] = v
        elif channel.upper() == "K":
            new_cmyk[3] = v
        return tuple(clamp_cmyk(new_cmyk))

    def channel_value(self, v):
        if self.labels_in_pct:
            return "%.0f" % (v * 100.0)
        return "%.2f" % (v)

    def set_centre_cmyk(self, cmyk):
        v = self.inc_channel(cmyk, self.col_channel, -self.cols / 2 * self.col_inc)
        v = self.inc_channel(v, self.row_channel, -self.rows / 2 * self.row_inc)
        self.top_left_cmyk = clamp_cmyk(v)

    def set_col_range(self, cmyk_range, end=None):
        if isinstance(cmyk_range, (list, tuple)):
            start, end = cmyk_range[0], cmyk_range[1]
        elif end is not None:
            start = cmyk_range
        self.top_left_cmyk = self.set_cmyk_channel(
            self.top_left_cmyk, start, self.col_channel
        )
        if self.cols > 1:
            self.col_inc = (end - start) / (self.cols - 1)

    def set_row_range(self, cmyk_range, end=None):
        if isinstance(cmyk_range, (list, tuple)):
            start, end = cmyk_range[0], cmyk_range[1]
        elif end is not None:
            start = cmyk_range
        self.top_left_cmyk = self.set_cmyk_channel(
            self.top_left_cmyk, start, self.row_channel
        )
        if self.rows > 1:
            self.row_inc = (end - start) / (self.rows - 1)

    def draw_in_canvas(self, c):
        w = self.rect.width
        h = self.rect.height
        self.clear()
        # add a row + col if using labels
        if self.labels:
            h += h / self.rows
            hr = h / (self.rows + 1)
            w += w / self.cols
            wc = w / (self.cols + 1)
        else:
            hr = h / self.rows
            wc = w / self.cols
        CMYK = copy.copy(self.top_left_cmyk)

        if self.labels:
            # Title with reference value
            row_height = 0.5 / (self.rows + 1)
            rc = TableRow(0, 0)
            label = "CMYK = %s, %s, %s, %s" % (
                tuple(self.channel_value(CMYK[c]) for c in range(4))
            )
            tl = TextRect(0, 0, label, style=self.label_style)
            tl.style["horz-align"] = "left"
            rc.add_column("Title", tl)
            rc.set_column_width("Title", CONTENT_SIZE)
            tl = TextRect(
                0, 0, "%s" % (self.col_channel.upper()), style=self.label_style
            )
            tl.style["horz-align"] = "centre"
            rc.add_column("ColCh", tl)
            self.add_row("Titles", rc)
            self.set_row_height("Titles", row_height)

            # column-wise channel labels
            rc = TableRow(0, 0)
            tl = TextRect(
                0, 0, "%s" % (self.row_channel.upper()), style=self.label_style
            )
            rc.add_column("RowCh", tl)
            v = self.get_cmyk_channel(CMYK, self.col_channel)
            for col in range(self.cols):
                tl = TextRect(0, 0, self.channel_value(v), style=self.label_style)
                tl.style["border-line-left"] = True
                tl.style["border-line-right"] = True
                rc.add_column("L%d" % (col), tl)
                v += self.col_inc
            self.add_row("Labels", rc)
            self.set_row_height("Labels", row_height)

        for row in range(self.rows):
            rc = TableRow(w, hr)
            CMYK_start = copy.copy(CMYK)
            v = self.get_cmyk_channel(CMYK, self.row_channel)
            if self.labels:
                # row channel value labels
                tl = TextRect(wc, hr, self.channel_value(v), style=self.label_style)
                tl.style["border-line-top"] = True
                tl.style["border-line-bottom"] = True
                rc.add_column("L%d" % (row), tl)
                v += self.row_inc
            for col in range(self.cols):
                cr = ContentRect(wc, hr)
                cr.style["background-fill"] = True
                cr.style["background-colour"] = CMYK
                cr.style.set_all_margins(self.padding)
                rc.add_column("Cell%d%d" % (row, col), cr)
                CMYK = self.inc_channel(CMYK, self.col_channel, self.col_inc)
            self.add_row("Row%d" % (row), rc)
            CMYK = self.inc_channel(CMYK_start, self.row_channel, self.row_inc)
        super().draw_in_canvas(c)
