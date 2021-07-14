#! /usr/bin/env python3
#
# Copyright (C) 2020  Michael Gale
# This file is part of the legocad python module.
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

from reportlab.pdfgen import canvas

from toolbox import *
from pdfdoc import *


class TableVector:
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

    def __len__(self):
        return len(self.cells)

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
                if cell_label == cell.label:
                    if not only_visible or cell.visible:
                        yield cell

    def is_cell_overlapped(self, label):
        """Determines if cell overlapped any of its peers."""
        if not self.is_cell_visible(label):
            return False
        other_cells = []
        for cell in self.iter_cells():
            if not cell.label == label:
                other_cells.append(cell.label)
        r1 = self.get_cell_rect(label)
        if r1 is not None:
            for other in other_cells:
                r2 = self.get_cell_rect(other)
                if r1.overlaps(r2):
                    return True
        return False

    def has_overlapped_cells(self):
        """Determines if any child cells mutually overlap."""
        other_cells = []
        for cell in self.iter_cells():
            other_cells.append(cell.label)
        for cell in self.iter_cells():
            for other in other_cells:
                r1 = self.get_cell_rect(cell.label)
                if not other == cell.label:
                    r2 = self.get_cell_rect(other)
                    if r1.overlaps(r2):
                        return True
        return False

    def is_cell_clipped(self, label, tol=1e-2):
        """Determines if a cell is clipped by its parent."""
        if not self.is_cell_visible(label):
            return False
        r1 = self.get_cell_rect(label)
        if r1.left < self.rect.left:
            if abs(r1.left - self.rect.left) > tol:
                return True
        if r1.right > self.rect.right:
            if abs(r1.right - self.rect.right) > tol:
                return True
        if r1.top > self.rect.top:
            if abs(r1.top - self.rect.top) > tol:
                return True
        if r1.bottom < self.rect.bottom:
            if abs(r1.bottom - self.rect.bottom) > tol:
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
        w, h = self.get_content_size()
        total_area = w * h
        content_area = 0
        for cell in self.iter_cells():
            r = self.get_cell_rect(cell.label)
            content_area += r.width * r.height
        if total_area > 0:
            return (total_area - content_area) / total_area
        return 1.0

    def get_cell(self, label):
        for cell in self.cells:
            if cell.label == label:
                return cell
        return None

    def clear(self):
        self.cells = []
        self.cell_order = []
        self.overlay_content = None

    def get_cell_rect(self, label):
        cell = self.get_cell(label)
        return cell.content.rect if cell is not None else None

    def get_cell_inset_rect(self, label):
        cell = self.get_cell(label)
        if cell is not None:
            r = cell.content.style.get_inset_rect(cell.content.rect)
            return r
        return None

    def get_cell_margin_rect(self, label):
        cell = self.get_cell(label)
        if cell is not None:
            r = cell.content.style.get_margin_rect(cell.content.rect)
            return r
        return None

    def set_cell_rect(self, label, rect):
        cell = self.get_cell(label)
        if cell is not None:
            cell.content.rect = rect

    def get_cell_rects(self, as_is=False):
        rects = []
        for cell in self.iter_cells():
            if as_is:
                rects.append(cell.content.rect)
            else:
                cw, ch = cell.content.get_content_size()
                r = Rect(cw, ch)
                rects.append(r)
        return rects

    def get_cell_constraints(self, label):
        cell = self.get_cell(label)
        return cell.constraints

    def set_cell_constraints(self, label, constraints, order=None):
        cell = self.get_cell(label)
        if cell is not None:
            cell.constraints = constraints
        if order is not None:
            cell.order = order

    def get_cell_content(self, label):
        cell = self.get_cell(label)
        return cell.content if cell is not None else None

    def set_cell_content(self, label, content):
        cell = self.get_cell(label)
        cell.content = content

    def is_cell_visible(self, label):
        cell = self.get_cell(label)
        return cell.visible if cell is not None else False

    def set_cell_visible(self, label, is_visible=True):
        cell = self.get_cell(label)
        if cell is not None:
            cell.visible = is_visible

    def set_cell_order(self, label, order):
        cell = self.get_cell(label)
        if cell is not None:
            cell.order = order

    def compute_cell_order(self):
        order = []
        labels = []
        for cell in self.cells:
            order.append(cell.order)
            labels.append(cell.label)
        cells = zip(order, labels)
        ocells = sorted(cells, key=lambda x: x[0])
        self.cell_order = []
        for cell in ocells:
            self.cell_order.append(cell[1])

    def compute_cell_sizes(self, axis="width"):
        self.compute_cell_order()
        cell_rect = self.style.get_inset_rect(self.rect)
        if axis == "width":
            total_limit = cell_rect.width
        else:
            total_limit = cell_rect.height
        acc_size = 0
        unassigned = []

        # set cell size for cells with a specification
        for cell in self.iter_cells():
            if axis == "width":
                if cell.width > 0:
                    cwidth = cell.width * total_limit
                    cell.content.rect.set_size(cwidth, cell_rect.height)
                    acc_size += cwidth
                elif cell.width == CONTENT_SIZE:
                    cw, ch = cell.content.get_content_size()
                    # cw += cell.content.style.get_width_trim()
                    cell.content.rect.set_size(cw, cell_rect.height)
                    acc_size += cw
                else:
                    unassigned.append(cell.label)
            else:
                if cell.height > 0:
                    cheight = cell.height * total_limit
                    cell.content.rect.set_size(cell_rect.width, cheight)
                    acc_size += cheight
                elif cell.height == CONTENT_SIZE:
                    cw, ch = cell.content.get_content_size()
                    # ch += cell.content.style.get_height_trim()
                    cell.content.rect.set_size(cell_rect.width, ch)
                    acc_size += ch
                else:
                    unassigned.append(cell.label)

        # set cell sizes for remaining cells automatically
        # based on the remaining space in the table vector
        rem_size = total_limit - acc_size
        for ucell in unassigned:
            if rem_size > 0:
                csize = rem_size / len(unassigned)
            else:
                csize = 0
            for cell in self.cells:
                if cell.label == ucell and cell.visible:
                    if axis == "width":
                        cell.content.rect.set_size(csize, cell_rect.height)
                    else:
                        cell.content.rect.set_size(cell_rect.width, csize)
                    acc_size += csize

        # move each cells's origin based on the cell order
        inv_valign = (
            True
            if axis == "height" and self.style.get_attr("vert-align") == "bottom"
            else False
        )
        inv_halign = (
            True
            if axis == "width" and self.style.get_attr("horz-align") == "right"
            else False
        )
        cy = cell_rect.bottom if inv_valign else cell_rect.top
        cx = cell_rect.right if inv_halign else cell_rect.left
        ordered = (
            self.cell_order
            if (not inv_valign and not inv_halign)
            else reversed(self.cell_order)
        )
        for cell_label in ordered:
            for cell in self.cells:
                if cell_label == cell.label and cell.visible:
                    if inv_valign:
                        cy += cell.content.rect.height
                    if inv_halign:
                        cx -= cell.content.rect.width
                    cell.content.rect.move_top_left_to(Point(cx, cy))
                    if axis == "width" and not inv_halign:
                        cx += cell.content.rect.width
                    if axis == "height" and not inv_valign:
                        cy -= cell.content.rect.height
        self.assign_cell_overlay_content_rects()

    def draw_border_lines(self, c):
        border_colour = self.style.get_attr("border-colour", (1, 1, 1))
        border_width = self.style.get_attr("border-width", 0)
        c.setStrokeColor(rl_colour(border_colour))
        c.setLineWidth(border_width)
        mrect = self.style.get_margin_rect(self.rect)
        if self.style.get_attr("border-line-left", False):
            c.line(mrect.left, mrect.top, mrect.left, mrect.bottom)
        if self.style.get_attr("border-line-right", False):
            c.line(mrect.right, mrect.top, mrect.right, mrect.bottom)
        if self.style.get_attr("border-line-top", False):
            c.line(mrect.left, mrect.top, mrect.right, mrect.top)
        if self.style.get_attr("border-line-bottom", False):
            c.line(mrect.left, mrect.bottom, mrect.right, mrect.bottom)

    def draw_debug_rect(self, c, r, colour=(0, 0, 0)):
        c.setFillColor(rl_colour_trans())
        c.setStrokeColor(rl_colour(colour))
        c.setLineWidth(0.1)
        c.rect(r.left, r.bottom, r.width, r.height, stroke=True, fill=False)

    def draw_background(self, c):
        has_background = self.style.get_attr("background-fill", False)
        background_colour = self.style.get_attr("background-colour", (1, 1, 1))
        if has_background:
            fc = rl_colour(background_colour)
            c.setFillColor(fc)
        else:
            fc = rl_colour_trans()
        has_border = self.style.get_attr("border-outline", False)
        if has_border:
            border_colour = self.style.get_attr("border-colour", (1, 1, 1))
            border_width = self.style.get_attr("border-width", 0)
            rc = rl_colour(border_colour)
            c.setStrokeColor(rc)
            c.setLineWidth(border_width)
        mrect = self.style.get_margin_rect(self.rect)
        border_radius = self.style.get_attr("border-radius", 0)
        if border_radius > 0:
            c.roundRect(
                mrect.left,
                mrect.bottom,
                mrect.width,
                mrect.height,
                radius=border_radius,
                stroke=has_border,
                fill=has_background,
            )
        else:
            c.rect(
                mrect.left,
                mrect.bottom,
                mrect.width,
                mrect.height,
                stroke=has_border,
                fill=has_background,
            )

    def assign_cell_overlay_content_rects(self):
        for cell in self.iter_cells():
            # assign each cell's overlay content if applicable
            if cell.content.overlay_content is not None:
                if cell.content.style.get_attr("overlay-size") == "auto":
                    cell.content.overlay_content.rect = cell.content.rect
                else:
                    cw = cell.content.rect.width
                    ch = cell.content.rect.height
                    ow = cell.content.overlay_content.rect.width
                    oh = cell.content.overlay_content.rect.height
                    if cell.content.style.get_attr("overlay-horz-align") == "left":
                        ox = cell.content.rect.left
                    elif cell.content.style.get_attr("overlay-horz-align") == "right":
                        ox = cell.content.rect.right - ow
                    else:
                        ox = cell.content.rect.left + cw / 2 - ow / 2
                    if cell.content.style.get_attr("overlay-vert-align") == "top":
                        oy = cell.content.rect.top
                    elif cell.content.style.get_attr("overlay-vert-align") == "bottom":
                        oy = cell.content.rect.bottom
                    else:
                        oy = cell.content.rect.top + ch / 2 - oh / 2
                    cell.content.overlay_content.rect.move_top_left_to(Point(ox, oy))
        # finally assign overlay content rect
        if self.overlay_content is not None:
            self.overlay_content.rect = self.style.get_inset_rect(self.rect)

    def draw_cells_in_canvas(self, canvas, axis):
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
            self.draw_debug_rect(canvas, self.rect)
            inset_rect = self.style.get_inset_rect(self.rect)
            self.draw_debug_rect(canvas, inset_rect, (0, 0, 1))
