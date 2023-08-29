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
# LayoutCell class

from toolbox import *
from pdfdoc import *

CONSTRAINT_TOKENS = (
    "left",
    "right",
    "top",
    "bottom",
    "left_quarter",
    "right_quarter",
    "top_quarter",
    "bottom_quarter",
    "mid_width",
    "mid_height",
    "above",
    "below",
    "rightof",
    "leftof",
    "right_of",
    "left_of",
    "centre",
    "center",
    "middleof",
    "middle_of",
    "resize",
    "between_horz",
    "between_vert",
    "between",
    "horz_pos",
    "vert_pos",
    "left_bound",
    "right_bound",
    "top_bound",
    "bottom_bound",
)
SINGLE_TOKENS = (
    "above",
    "below",
    "rightof",
    "leftof",
    "right_of",
    "left_of",
    "middle_of",
    "middleof",
    "left_bound",
    "right_bound",
    "top_bound",
    "bottom_bound",
)
ABS_TOKENS = ("horz_pos", "vert_pos")
BETWEEN_TOKENS = ("between", "between_horz", "between_vert")
OTHER_TOKENS = (
    "to",
    "and",
    "parent_right",
    "parent_left",
    "parent_bottom",
    "parent_top",
)


def extract_labels(constraint, token_list=None):
    """Extracts strings from constraint which are not tokens in CONSTRAINT_TOKENS or
    SINGLE_TOKENS.  These extracted strings are labels of other cells."""
    tokens = token_list if token_list is not None else CONSTRAINT_TOKENS
    c = constraint.split()
    return [e for e in c if e not in tokens]


def split_with_token(constraint, token):
    c = constraint.split()
    cu = []
    for e in c:
        if e.lower() == token.lower():
            cu.append(token.upper())
        else:
            cu.append(e)
    c = " ".join(cu)
    c = c.split(token.upper())
    return c


def parse_constraint(constraint):
    """Parses a constraint into a dictionary which describes the source/from
    point (from_pt) and where it should be transformed to (dest_pt).  Optional
    labels describing which cell(s) the destination point is referring to are
    also extracted."""
    cdict = {"from_pt": None, "dest_pt": None, "dest_labels": []}
    c = constraint.lower()
    for token in ABS_TOKENS:
        if token in c:
            cdict["abs_pos"] = token
            cdict["abs_val"] = extract_labels(constraint)
            return cdict
    for token in SINGLE_TOKENS:
        if token in c:
            cdict["dest_pt"] = token
            cdict["dest_labels"] = extract_labels(constraint)
            return cdict
    for token in BETWEEN_TOKENS:
        if token in c.split():
            cb = split_with_token(constraint, "and")
            if len(cb) == 2:
                g1 = extract_labels(cb[0])
                g2 = extract_labels(cb[1])
                cdict[token] = {"group1": g1, "group2": g2}
                return cdict

    c = split_with_token(constraint, "to")
    if len(c) == 2:
        other = extract_labels(c[1])
        if len(other) > 0:
            cdict["from_pt"] = c[0]
            d = c[1]
            for e in other:
                d = d.replace(e, "")
            cdict["dest_pt"] = d.lstrip()
            cdict["dest_labels"] = other
        else:
            cdict["from_pt"] = c[0]
            cdict["dest_pt"] = c[1].lstrip()
    else:
        cdict["from_pt"] = c[0]
        cdict["dest_pt"] = c[0].lstrip()
    return cdict


def dummy_rect_from_parent_edge(parent_rect, edges):
    edges = edges.split("_")
    x, y = parent_rect.get_centre()
    valid = False
    for e in edges:
        if e == "left":
            x = parent_rect.left
            valid = True
        elif e == "right":
            x = parent_rect.right
            valid = True
        elif e == "top":
            y = parent_rect.top
            valid = True
        elif e == "bottom":
            y = parent_rect.bottom
            valid = True
    if valid:
        drect = Rect(0, 0)
        drect.move_to((x, y))
        return drect
    return None


class LayoutCell(TableVector):
    """A LayoutCell is a sub-class of TableVector.  It contains one or more TableCells
    (with content as a ContentRect type).  LayoutCell is populated by constraints
    describing a cell's relationship to the parent container (self) and/or other
    sibling TableCell items.  Each constraint is a string description of how one or
    more anchor points in the cell's rectangle should be placed relative to either
    the parent container rectangle or another cell's rectangle.
    Examples:
            "top left" - top left corner aligned to parent top left container rect
            "bottom right to centre" - bottom right corner aligned to parent's centre
            "below Cell2" - cell rectangle placed below Cell2's rectangle
            "above Cell1 Cell3" - cell rectangle placed above both Cell1 and Cell3
            "between Cell1 and Cell2 parent_right"
        In general constraints are in the form of:
            <my ref point> TO <parent ref point>
        or  <my ref point> TO <label ref point>
        or  below, above, rightof, leftof <[labels]>
    """

    def __init__(self, w=0, h=0, style=None, **kwargs):
        super().__init__(w, h, style)
        self.width_constraint = w
        self.height_constraint = h
        self.parse_kwargs(**kwargs)

    def __str__(self):
        s = []
        s.append("LayoutCell: %r" % (self))
        s.append("  Cell count: %d" % (len(self.cells)))
        s.append("  Rect: %s" % (str(self.rect)))
        s.append("  Overlay content: %r" % (self.overlay_content))
        s.append("  Show debug rects: %s" % (self.show_debug_rects))
        s.append(
            "  Width/height constraint: %.1f, %.1f"
            % (self.width_constraint, self.height_constraint)
        )
        s.append(
            "  Width/height total: %.1f, %.1f" % (self.total_width, self.total_height)
        )
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
                s.append("      constraints: %s" % (cell.constraints))
            idx += 1
        return "\n".join(s)

    def compute_cell_order(self):
        """Reorder cells so that cells without sibling dependancies are first
        followed by cells with mutual dependancies."""
        peer_labels = []
        for cell in self.cells:
            if cell.constraints is None:
                continue
            elabels = []
            for c in cell.constraints:
                e = extract_labels(
                    c, [*CONSTRAINT_TOKENS, *SINGLE_TOKENS, *OTHER_TOKENS]
                )
                elabels.extend(e)
            peer_labels.append([cell.label, elabels])
        pn = len(peer_labels)
        for i in range(0, pn - 1):
            for j in range(i + 1, pn):
                if peer_labels[j][0] in peer_labels[i][1]:
                    peer_labels[i], peer_labels[j] = peer_labels[j], peer_labels[i]
        self.cell_order = []
        for i, cell in enumerate(peer_labels):
            self.cell_order.append(cell[0])
            self.set_cell_order(cell[0], i)

    def layout_cells(self):
        def _collect_rects(cells, parent_rect):
            rects = []
            for cell in cells:
                if self.is_cell_visible(cell):
                    rects.append(self.get_cell_rect(cell))
                else:
                    pr = dummy_rect_from_parent_edge(parent_rect, cell)
                    if pr is not None:
                        rects.append(pr)
            return rects

        w = self.fixed_rect.width if self.is_fixed_width else self.rect.width
        h = self.fixed_rect.height if self.is_fixed_height else self.rect.height
        self.rect.set_size_anchored(w, h, anchor_pt="top left")
        prect = self.style.get_inset_rect(self.rect)
        for cell in self.iter_cells():
            crect = self.get_cell_rect(cell.label)
            if cell.constraints is None:
                # default to top left of parent container if no constraints are specified
                crect = self.get_cell_rect(cell.label)
                crect.anchor_with_constraint(prect, "top left to top left")
                self.set_cell_rect(cell.label, crect)
                continue
            for c in cell.constraints:
                cd = parse_constraint(c)
                if any([token in cd for token in BETWEEN_TOKENS]):
                    bt = "between" if "between" in cd else ""
                    bt = "between_horz" if "between_horz" in cd else bt
                    bt = "between_vert" if "between_vert" in cd else bt
                    g1r = _collect_rects(cd[bt]["group1"], prect)
                    g2r = _collect_rects(cd[bt]["group2"], prect)
                    if len(g1r) > 0 and len(g2r) > 0:
                        g1_rect = Rect.bounding_rect_from_rects(g1r)
                        g2_rect = Rect.bounding_rect_from_rects(g2r)
                        if "between_vert" in cd or "between" in cd:
                            if g1_rect.bottom > g2_rect.top:
                                mid_y = g2_rect.top + (g1_rect.bottom - g2_rect.top) / 2
                            else:
                                mid_y = g1_rect.top + (g2_rect.bottom - g1_rect.top) / 2
                            crx, cry = crect.get_centre()
                            crect.move_to((crx, mid_y))
                        if "between_horz" in cd or "between" in cd:
                            if g1_rect.right < g2_rect.left:
                                mid_x = (
                                    g1_rect.right + (g2_rect.left - g1_rect.right) / 2
                                )
                            else:
                                mid_x = (
                                    g2_rect.right + (g1_rect.left - g2_rect.right) / 2
                                )
                            crx, cry = crect.get_centre()
                            crect.move_to((mid_x, cry))
                elif len(cd["dest_labels"]) > 0:
                    others = []
                    for dest in cd["dest_labels"]:
                        if self.is_cell_visible(dest):
                            dest_rect = self.get_cell_rect(dest)
                            others.append(dest_rect)
                        else:
                            pr = dummy_rect_from_parent_edge(prect, dest)
                            if pr is not None:
                                others.append(pr)
                    other_rect = Rect.bounding_rect_from_rects(others)
                    if cd["from_pt"] is not None:
                        crect.anchor_with_constraint(
                            other_rect, cd["from_pt"] + " to " + cd["dest_pt"]
                        )
                    else:
                        if "bound" in cd["dest_pt"].lower().split("_"):
                            crect.shove_with_constraint(other_rect, cd["dest_pt"])
                        else:
                            crect.anchor_with_constraint(other_rect, cd["dest_pt"])
                elif "abs_pos" in cd:
                    if cd["abs_pos"] == "horz_pos":
                        rect_mid = crect.get_centre()
                        horz_pos = float(cd["abs_val"][0]) + prect.left
                        crect.move_to(horz_pos, rect_mid[1])
                    elif cd["abs_pos"] == "vert_pos":
                        rect_mid = crect.get_centre()
                        vert_pos = prect.top - float(cd["abs_val"][0])
                        crect.move_to(rect_mid[0], vert_pos)
                else:
                    if cd["from_pt"] is not None:
                        crect.anchor_with_constraint(
                            prect, cd["from_pt"] + " to " + cd["dest_pt"]
                        )
                    else:
                        crect.anchor_with_constraint(prect, cd["dest_pt"])
            self.set_cell_rect(cell.label, crect)

    def add_cell(self, label, content, order=None, constraints=None):
        if order is not None:
            cell = TableCell(label, content, order, 0, 0)
        else:
            cell = TableCell(label, content, len(self.cells), 0, 0)
        cell.constraints = constraints
        self.cells.append(cell)

    def recompute_layout(self, with_padding=True):
        _, _ = self.get_content_size(with_padding=with_padding)

    def get_content_size(self, with_padding=True):
        self.compute_cell_layout(with_padding=with_padding)
        if self.is_fixed_width:
            self.total_width = self.fixed_rect.width
        if self.is_fixed_height:
            self.total_height = self.fixed_rect.height
        if self.min_width:
            self.total_width = max(self.total_width, self.min_width)
        if self.min_height:
            self.total_height = max(self.total_height, self.min_height)
        return self.total_width, self.total_height

    def compute_cell_layout(self, with_padding=True):
        self.compute_cell_order()
        rpt = self.top_left
        for cell in self.iter_cells():
            self.set_cell_rect(cell.label, Rect(*cell.content.get_content_size()))
        self.layout_cells()
        bounds = Rect.bounding_rect_from_rects(self.get_cell_rects(as_is=True))
        self.total_width = bounds.width
        self.total_height = bounds.height
        if with_padding:
            self.total_width += self.style.width_pad_margin
            self.total_height += self.style.height_pad_margin
        self.rect.set_size(self.total_width, self.total_height)
        self.top_left = rpt
        self.assign_cell_overlay_content_rects()

    def draw_in_canvas(self, canvas):
        self.draw_cells_in_canvas(canvas)

    def draw_cells_in_canvas(self, canvas):
        self.compute_cell_layout()
        super().draw_cells_in_canvas(canvas, axis=None)
        if self.show_debug_rects:
            rw = Rect(self.width_constraint, 1)
            rh = Rect(1, self.height_constraint)
            rw.move_top_left_to((self.rect.left, self.rect.top))
            rh.move_top_left_to((self.rect.left, self.rect.top))
            self.draw_debug_rect(canvas, rw, (1, 0, 1))
            self.draw_debug_rect(canvas, rh, (1, 0, 1))
