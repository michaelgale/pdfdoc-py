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
# TableVector container class

import random
import string

from toolbox import *
from pdfdoc import *


class TableVector(DocStyleMixin, RectMixin):
    def __init__(self, w=0, h=0, style=None):
        self.rect = Rect()
        self.rect.set_size(w, h)
        self.clip_text = False
        self.style = DocStyle()
        if style is not None:
            self.style.set_with_dict(style)
        self.cells = []
        self.cell_order = []
        self.overlay_content = None
        self.show_debug_rects = False
        self.total_width = 0
        self.total_height = 0
        self.is_fixed_width = False
        self.is_fixed_height = False
        self.fixed_rect = Rect(w, h)
        self.min_width = 0
        self.min_height = 0

    def parse_kwargs(self, **kwargs):
        for k, v in kwargs.items():
            if k in self.__dict__:
                self.__dict__[k] = v
            elif k in RectMixin.__dict__:
                if k == "top_left":
                    self.top_left = v
                elif k == "top_right":
                    self.top_right = v
                elif k == "bottom_left":
                    self.bottom_left = v
                elif k == "bottom_right":
                    self.bottom_right = v
                elif k == "centre":
                    self.centre = v
            else:
                self.style[k] = v

    def __len__(self):
        return len(self.cells)

    def __repr__(self):
        return "%s(%.2f, %.2f)" % (
            self.__class__.__name__,
            self.rect.width,
            self.rect.height,
        )

    def __str__(self):
        s = []
        s.append("TableVector: %r" % (self))
        s.append("  Cell count: %d" % (len(self.cells)))
        s.append("  Rect: %s" % (str(self.rect)))
        w, h = self.get_content_size()
        s.append("  Content size: %.1f, %.1f" % (w, h))
        clipped = self.has_clipped_cells()
        overlapped = self.has_overlapped_cells()
        ratio = self.get_whitespace_ratio()
        s.append("  Clipped cells: %s Overlapped cells: %s" % (clipped, overlapped))
        s.append("  Whitespace ratio: %.1f%%" % (ratio * 100.0))
        s.append("  Overlay content: %r" % (self.overlay_content))
        s.append("  Show debug rects: %s" % (self.show_debug_rects))
        idx = 1
        for cell in self.iter_cells(only_visible=False):
            s.append(
                "  %d. Cell(%-12s) order=%-2d visible=%-5s type=%r"
                % (idx, cell.label, cell.order, cell.visible, cell.content)
            )
            if cell.visible:
                s.append(
                    "      rect: %s content size: (%.1f, %.1f)"
                    % (cell.content.rect, *cell.content.get_content_size())
                )
            idx += 1
        return "\n".join(s)

    def iter_cells(self, only_visible=True):
        self.compute_cell_order()
        for cell_label in self.cell_order:
            for cell in self.cells:
                if not cell_label == cell.label:
                    continue
                if not only_visible or cell.visible:
                    yield cell

    def is_cell_on_transparent_rect(self, cell, other):
        """Determines if other cell safely overlaps a transparent region
        of a cell with an ImageRect."""
        c1 = self[cell].content
        c2 = self[other].content
        if isinstance(c1, ImageRect):
            img_cell, img_label = c1, cell
            other_cell, other_label = c2, other
        elif isinstance(c2, ImageRect):
            img_cell, img_label = c2, other
            other_cell, other_label = c1, cell
        else:
            return False
        if not self[other_label].can_overlap:
            return False
        other_rect_pix = img_cell.convert_rect_to_pix(other_cell.rect)
        overlap = is_rect_in_transparent_region(img_cell.filename, other_rect_pix)
        return overlap

    def is_cell_overlapped(self, label):
        """Determines if cell overlapped any of its peers."""
        if not self.is_cell_visible(label):
            return False
        other_cells = [c.label for c in self.iter_cells() if not c.label == label]
        r1 = self.get_cell_rect(label)
        if r1 is None:
            return False
        for other in other_cells:
            if r1.overlaps(self.get_cell_rect(other)):
                if not self.is_cell_on_transparent_rect(label, other):
                    return True
        return False

    def has_overlapped_cells(self):
        """Determines if any child cells mutually overlap."""
        other_cells = [cell.label for cell in self.iter_cells()]
        for cell in self.iter_cells():
            for other in other_cells:
                if other == cell.label:
                    continue
                r1 = self.get_cell_rect(cell.label)
                if r1.overlaps(self.get_cell_rect(other)):
                    if not self.is_cell_on_transparent_rect(cell.label, other):
                        return True
        return False

    def is_cell_clipped(self, label, tol=1e-2):
        """Determines if a cell is clipped by its parent."""
        if not self.is_cell_visible(label):
            return False
        r1 = self.get_cell_rect(label)
        if r1.left < self.rect.left and abs(r1.left - self.rect.left) > tol:
            return True
        if r1.right > self.rect.right and abs(r1.right - self.rect.right) > tol:
            return True
        if r1.top > self.rect.top and abs(r1.top - self.rect.top) > tol:
            return True
        if r1.bottom < self.rect.bottom and abs(r1.bottom - self.rect.bottom) > tol:
            return True
        return False

    def has_clipped_cells(self, tol=1e-2):
        """Determines if any child cells extend outside the parent container."""
        all_rects = self.get_cell_rects(as_is=True)
        brect = Rect.bounding_rect_from_rects(all_rects)
        if brect.left < self.rect.left:
            if abs(brect.left - self.rect.left) > tol:
                return True
        if brect.right > self.rect.right:
            if abs(brect.right - self.rect.right) > tol:
                return True
        if brect.top > self.rect.top:
            if abs(brect.top - self.rect.top) > tol:
                return True
        if brect.bottom < self.rect.bottom:
            if abs(brect.bottom - self.rect.bottom) > tol:
                return True
        return False

    def get_whitespace_ratio(self):
        """Returns the ratio of whitespace (unoccupied space) to space occupied
        by cells in the TableVector parent container.  A value of 1.0 indicates
        a completely blank space and 0.0 indicates a fully occupied space."""
        total_area = self.rect.area
        content_area = sum(
            [self.get_cell_rect(c.label).area for c in self.iter_cells()]
        )
        if total_area > 0:
            return (total_area - content_area) / total_area
        return 1.0

    def __getitem__(self, key):
        return self.get_cell(key)

    def get_cell(self, label):
        for cell in self.cells:
            if cell.label == label:
                return cell
        return None

    def add_cell(self, label, content, order=None, height=None, width=None):
        order = order if order is not None else len(self.cells)
        width = width if width is not None else AUTO_SIZE
        height = height if height is not None else AUTO_SIZE
        cell = TableCell(label, content, order, width=width, height=height)
        self.cells.append(cell)

    def add_content(self, content=None, order=None, height=None, width=None):
        """An alternate to add_cell which does not require a label name.
        The label name is automatically assigned."""
        if content is None:
            label = "".join(random.choice(string.ascii_lowercase) for _ in range(8))
        else:
            label = str(content.__hash__())
        self.add_cell(label, content=content, order=order, height=height, width=width)

    def clear(self):
        self.cells = []
        self.cell_order = []
        self.overlay_content = None

    def get_cell_rect(self, label):
        cell = self[label]
        return cell.content.rect if cell is not None else None

    @property
    def inset_rect(self):
        return self.style.get_inset_rect(self.rect)

    @property
    def margin_rect(self):
        return self.style.get_margin_rect(self.rect)

    def get_cell_inset_rect(self, label):
        cell = self[label]
        if cell is not None:
            return cell.content.inset_rect
        return None

    def get_cell_margin_rect(self, label):
        cell = self[label]
        if cell is not None:
            return cell.content.margin_rect
        return None

    def set_cell_rect(self, label, rect):
        cell = self[label]
        if cell is not None:
            cell.content.rect = rect

    def get_cell_rects(self, as_is=False):
        rects = []
        for cell in self.iter_cells():
            if as_is:
                rects.append(cell.content.rect)
            else:
                rects.append(Rect(*cell.content.get_content_size()))
        return rects

    def get_cell_constraints(self, label):
        return self[label].constraints

    def set_cell_constraints(self, label, constraints, order=None):
        cell = self[label]
        if cell is not None:
            cell.constraints = constraints
        if order is not None:
            cell.order = order

    def get_cell_content(self, label):
        cell = self[label]
        return cell.content if cell is not None else None

    def set_cell_content(self, label, content):
        self[label].content = content

    def is_cell_visible(self, label):
        cell = self[label]
        return cell.visible if cell is not None else False

    def set_cell_visible(self, label, is_visible=True):
        cell = self[label]
        if cell is not None:
            cell.visible = is_visible

    def set_cell_order(self, label, order):
        cell = self[label]
        if cell is not None:
            cell.order = order

    def compute_cell_order(self):
        order = [cell.order for cell in self.cells]
        labels = [cell.label for cell in self.cells]
        cells = zip(order, labels)
        ocells = sorted(cells, key=lambda x: x[0])
        self.cell_order = [cell[1] for cell in ocells]

    def compute_cell_sizes(self, axis="width"):
        self.compute_cell_order()
        cell_rect = self.style.get_inset_rect(self.rect)
        total_limit = cell_rect.width if axis == "width" else cell_rect.height
        acc_size = 0
        unassigned = []
        axis_width = axis == "width"
        cr_height = cell_rect.height
        cr_width = cell_rect.width

        # set cell size for cells with a specification
        for cell in self.iter_cells():
            if axis_width:
                if cell.width > 0:
                    cwidth = cell.width * total_limit
                    cell.content.size = (cwidth, cr_height)
                    acc_size += cwidth
                elif cell.width == CONTENT_SIZE:
                    cw, ch = cell.content.get_content_size()
                    # cw += cell.content.style.get_width_trim()
                    cell.content.size = (cw, cr_height)
                    acc_size += cw
                else:
                    unassigned.append(cell.label)
            else:
                if cell.height > 0:
                    cheight = cell.height * total_limit
                    cell.content.size = (cr_width, cheight)
                    acc_size += cheight
                elif cell.height == CONTENT_SIZE:
                    cw, ch = cell.content.get_content_size()
                    # ch += cell.content.style.get_height_trim()
                    cell.content.size = (cr_width, ch)
                    acc_size += ch
                else:
                    unassigned.append(cell.label)

        # set cell sizes for remaining cells automatically
        # based on the remaining space in the table vector
        rem_size = total_limit - acc_size
        if len(unassigned) > 0 and rem_size > 0:
            csize = rem_size / len(unassigned)
        else:
            csize = 0
        for ucell in unassigned:
            for cell in self.cells:
                if not (cell.label == ucell and cell.visible):
                    continue
                if axis == "width":
                    cell.content.size = (csize, cr_height)
                else:
                    cell.content.size = (cr_width, csize)
                acc_size += csize

        # move each cells's origin based on the cell order
        inv_valign = axis == "height" and self.style["vert-align"] == "bottom"
        inv_halign = axis == "width" and self.style["horz-align"] == "right"
        cy = cell_rect.bottom if inv_valign else cell_rect.top
        cx = cell_rect.right if inv_halign else cell_rect.left
        ordered = (
            self.cell_order
            if (not inv_valign and not inv_halign)
            else reversed(self.cell_order)
        )
        for cell_label in ordered:
            for cell in self.cells:
                if not (cell_label == cell.label and cell.visible):
                    continue
                if inv_valign:
                    cy += cell.content.rect.height
                if inv_halign:
                    cx -= cell.content.rect.width
                cell.content.top_left = (cx, cy)
                if axis == "width" and not inv_halign:
                    cx += cell.content.rect.width
                if axis == "height" and not inv_valign:
                    cy -= cell.content.rect.height
        self.assign_cell_overlay_content_rects()

    def get_content_size(self, with_padding=True):
        self.compute_cell_sizes()
        r = self.get_cell_rects(as_is=True)
        if len(r) > 0:
            rb = Rect.bounding_rect_from_rects(r)
        else:
            rb = Rect(0, 0)
        self.total_width = rb.width
        self.total_height = rb.height
        if with_padding:
            self.total_width += self.style.width_pad_margin
            self.total_height += self.style.height_pad_margin
        if self.is_fixed_width:
            self.total_width = self.fixed_rect.width
        if self.is_fixed_height:
            self.total_height = self.fixed_rect.height
        if self.min_width:
            self.total_width = max(self.total_width, self.min_width)
        if self.min_height:
            self.total_height = max(self.total_height, self.min_height)
        return self.total_width, self.total_height

    def draw_border_lines(self, c):
        border_colour = self.style["border-colour"]
        border_width = self.style["border-width"]
        c.setStrokeColor(rl_colour(border_colour))
        c.setLineWidth(border_width)
        mrect = self.style.get_margin_rect(self.rect)
        if self.style["border-line-left"]:
            c.line(mrect.left, mrect.top, mrect.left, mrect.bottom)
        if self.style["border-line-right"]:
            c.line(mrect.right, mrect.top, mrect.right, mrect.bottom)
        if self.style["border-line-top"]:
            c.line(mrect.left, mrect.top, mrect.right, mrect.top)
        if self.style["border-line-bottom"]:
            c.line(mrect.left, mrect.bottom, mrect.right, mrect.bottom)

    def draw_debug_rect(self, c, r, colour=None):
        lw = 0.5 if colour is None else 0.2
        dash = [1, 2, 1, 0] if colour is None else [0.5, 0.5, 0.5, 0]
        colour = colour if colour is not None else DEBUG_RECT_COLOUR
        c.saveState()
        c.setFillColor(rl_colour_trans())
        c.setStrokeColor(rl_colour(colour))
        c.setDash(dash)
        c.setLineWidth(lw)
        c.rect(r.left, r.bottom, r.width, r.height, stroke=True, fill=False)
        c.restoreState()

    def draw_background(self, c):
        rl_draw_rect(c, self.rect, self.style)

    def assign_cell_overlay_content_rects(self):
        for cell in self.iter_cells():
            # assign each cell's overlay content if applicable
            if cell.content.overlay_content is not None:
                if cell.content.style["overlay-size"] == "auto":
                    cell.content.overlay_content.rect = cell.content.rect
                else:
                    cw = cell.content.rect.width
                    ch = cell.content.rect.height
                    ow = cell.content.overlay_content.rect.width
                    oh = cell.content.overlay_content.rect.height
                    if cell.content.style["overlay-horz-align"] == "left":
                        ox = cell.content.rect.left
                    elif cell.content.style["overlay-horz-align"] == "right":
                        ox = cell.content.rect.right - ow
                    else:
                        ox = cell.content.rect.left + cw / 2 - ow / 2
                    if cell.content.style["overlay-vert-align"] == "top":
                        oy = cell.content.rect.top
                    elif cell.content.style["overlay-vert-align"] == "bottom":
                        oy = cell.content.rect.bottom
                    else:
                        oy = cell.content.rect.top + ch / 2 - oh / 2
                    cell.content.overlay_content.top_left = (ox, oy)
        # finally assign overlay content rect
        if self.overlay_content is not None:
            self.overlay_content.rect = self.style.get_inset_rect(self.rect)

    def draw_cells_in_canvas(self, canvas, axis=None):
        if axis is not None:
            self.compute_cell_sizes(axis)
        self.draw_background(canvas)
        if self.show_debug_rects:
            for cell in self.iter_cells():
                cell.content.show_debug_rects = True
        for cell in self.iter_cells():
            cell.content.draw_in_canvas(canvas)
        self.draw_border_lines(canvas)
        if self.overlay_content is not None:
            self.overlay_content.draw_in_canvas(canvas)
        if self.show_debug_rects:
            canvas.saveState()
            self.draw_debug_rect(canvas, self.rect)
            inset_rect = self.style.get_inset_rect(self.rect)
            self.draw_debug_rect(canvas, inset_rect, DEBUG_INSET_COLOUR)
            if self.is_fixed_height and self.is_fixed_width:
                self.draw_debug_rect(canvas, self.fixed_rect, (0, 1, 0))
            canvas.restoreState()

    @staticmethod
    def from_array(
        a,
        style=None,
        element_style=None,
        fit_to_contents=True,
        element_margin=0,
        **kwargs
    ):
        """
        Makes a TableVector instance from an array of text strings
        """
        from .tablecolumn import TableColumn
        from .tablerow import TableRow
        from pdfdoc.contentrect.textrect import TextRect

        v = TableColumn(style=style, fit_to_contents=fit_to_contents, **kwargs)
        sizing = CONTENT_SIZE if fit_to_contents else AUTO_SIZE
        for i, row in enumerate(a):
            if isinstance(row, str):
                r = TextRect(row, style=element_style)
            elif isinstance(row, (tuple, list)):
                r = TableRow(fit_to_contents=fit_to_contents)
                for j, c in enumerate(row):
                    if isinstance(c, str):
                        e = TextRect(c, style=element_style)
                    else:
                        e = c
                        if "auto_size" in c.__dict__:
                            c.auto_size = not fit_to_contents
                    if j + 1 < len(row):
                        e.right_margin = element_margin
                    r.add_column(e, width=sizing)
            else:
                r = row
                if "auto_size" in row.__dict__:
                    row.auto_size = not fit_to_contents
                    row.get_content_size()
            if i + 1 < len(a):
                r.bottom_margin = element_margin
            v.add_row(r, height=sizing)
        return v
