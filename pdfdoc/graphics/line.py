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
# Styled line

from toolbox import *
from pdfdoc import *
from pdfdoc.helpers import line_angle, line_mid_point


class StyledLine(DocStyleMixin):
    """Draws an arrow head with arbitrary style. The arrow can be placed
    and rotated in direction 0-360 deg."""

    def __init__(self, style=None, arrow_style=None):
        self.style = DocStyle()
        if style is not None:
            self.style.set_with_dict(style)
        self.coords = None
        self.use_default_arrow_style = True
        self.arrow = ArrowHead(style=arrow_style)
        if arrow_style is not None:
            self.use_default_arrow_style = False

    def __repr__(self):
        return "%s()" % (self.__class__.__name__,)

    @property
    def dash(self):
        return self.style["line-dash"]

    def draw_in_canvas(self, c, x0, y0, x1, y1, arrow0=False, arrow1=False):
        self.draw_from_coords(c, [(x0, y0), (x1, y1)], arrow0, arrow1)

    def draw_from_coords(self, c, coords=None, arrow0=False, arrow1=False):
        coords = coords if coords is not None else self.coords
        if coords is None:
            return
        self._prepare_line_style(c)
        # if the ends have arrows, modify the end points so that
        # they do not visibly protrude beyond the arrow head tip
        c0, c1 = coords[0], coords[-1]
        if arrow0:
            c0 = self.arrow.tip_offset(coords[0], coords[1], self.line_width)
        if arrow1:
            c1 = self.arrow.tip_offset(coords[-1], coords[-2], self.line_width)
        p = c.beginPath()
        p.moveTo(*c0)
        for coord in coords[1:-1]:
            p.lineTo(*coord)
        p.lineTo(*c1)
        c.drawPath(p, stroke=1, fill=0)
        if arrow0:
            self._draw_arrow_head(c, coords[0], coords[1])
        if arrow1:
            self._draw_arrow_head(c, coords[-1], coords[-2])
        self._reset_line_style(c)

    def _prepare_line_style(self, c):
        if isinstance(self.dash, list):
            c.setDash(array=self.dash)
        elif self.dash is not None:
            c.setDash(*self.dash)
        rc = rl_colour(self.style["line-colour"])
        c.setStrokeColor(rc)
        c.setLineWidth(self.line_width)
        if self.arrow.style["arrow-style"] == "cap":
            self.arrow.width = self.line_width
        if self.use_default_arrow_style:
            if not self.arrow.style["arrow-style"] == "cap":
                self.arrow.length = 8 * self.line_width
                self.arrow.width = 4.5 * self.line_width
            self.arrow.line_colour = self.line_colour
            self.arrow.line_width = self.line_width
            self.arrow.border_outline = False

    def _draw_arrow_head(self, c, p0, p1):
        angle = line_angle(p1, p0)
        self.arrow.draw_in_canvas(c, p0, angle, tip_origin=True)

    def _reset_line_style(self, c):
        c.setDash([])

    @staticmethod
    def draw_line(
        c,
        x0,
        y0,
        x1,
        y1,
        line_width=None,
        arrow0=False,
        arrow1=False,
        dash=None,
        style=None,
    ):
        line = StyledLine(style=style)
        if line_width is not None:
            line.style["line-width"] = line_width
        if dash is not None:
            line.style["line-dash"] = dash
        line.draw_in_canvas(c, x0, y0, x1, y1, arrow0, arrow1)

    @staticmethod
    def draw_dim_line(
        c, x0, y0, x1, y1, label, line_width=None, style=None, offset=None
    ):
        line = StyledLine(style=style)
        line.use_default_arrow_style = False
        if line_width is not None:
            line.style["line-width"] = line_width
        line.arrow.style["arrow-style"] = "dimension"
        line.arrow.length = 10 * line.line_width
        line.arrow.width = 6 * line.line_width
        line.arrow.line_width = line.line_width
        line.arrow.line_colour = line.line_colour
        line.draw_in_canvas(c, x0, y0, x1, y1, True, True)
        angle = line_angle((x0, y0), (x1, y1))
        mp = line_mid_point((x0, y0), (x1, y1))
        c.saveState()
        c.translate(*mp)
        c.rotate(angle)
        tr = TextRect(label, style=style, split_lines=False)
        _, th = tr.get_content_size()
        if offset is not None:
            tr.rect.move_to((0, offset))
        else:
            tr.rect.move_to((0, -th / 2))
        tr.draw_in_canvas(c)
        c.restoreState()

    @staticmethod
    def draw_arc(c, x0, y0, radius, a0, a1, line_width=None, dash=None, style=None):
        line = StyledLine(style=style)
        if line_width is not None:
            line.style["line-width"] = line_width
        if dash is not None:
            c.setDash(dash)
        c.setLineWidth(line.style["line-width"])
        rc = rl_colour(line.style["line-colour"])
        c.setStrokeColor(rc)
        p = c.beginPath()
        p.arc(
            x0 - radius,
            y0 - radius,
            x0 + radius,
            y0 + radius,
            startAng=a0,
            extent=(a1 - a0),
        )
        c.drawPath(p, stroke=1, fill=0)
        c.setDash([])

    @staticmethod
    def draw_grid(c, xo, yo, xs, ys, nx, ny, style=None):
        line = StyledLine(style=style)
        c.setLineWidth(line.style["grid-line-width"])
        rc = rl_colour(line.style["grid-line-colour"])
        c.setStrokeColor(rc)
        if isinstance(line.style["grid-dash"], list):
            c.setDash(array=line.style["grid-dash"])
        else:
            c.setDash(*line.style["grid-dash"])
        yc = yo + ny * ys
        for x in range(nx + 1):
            p = c.beginPath()
            xc = xo + x * xs
            p.moveTo(xc, yo)
            p.lineTo(xc, yc)
            c.drawPath(p, stroke=1, fill=0)
        xc = xo + nx * xs
        for y in range(ny + 1):
            p = c.beginPath()
            yc = yo + y * ys
            p.moveTo(xo, yc)
            p.lineTo(xc, yc)
            c.drawPath(p, stroke=1, fill=0)
        c.setDash([])
