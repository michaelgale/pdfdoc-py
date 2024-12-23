# Sample Test passing with nose and pytest

import os
import sys
import pytest
import random

from toolbox import *
from pdfdoc import *
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

_test_dict = {"left-margin": 1 * inch, "right-margin": 1 * inch, "horz-align": "left"}


_text_dict = {
    "border-outline": True,
    "border-width": 0.02 * inch,
    "border-colour": (1.0, 0.1, 0.2),
    "top-padding": 0.05 * inch,
    "bottom-padding": 0.05 * inch,
    "left-padding": 0.05 * inch,
    "right-padding": 0.05 * inch,
}


def test_layoutcell():
    tl = LayoutCell(6 * inch, 1 * inch)
    tl.style.set_with_dict(
        {
            "top-margin": 0.05 * inch,
            "bottom-margin": 0.1 * inch,
            "left-margin": 0.1 * inch,
            "right-margin": 0.05 * inch,
        }
    )
    tl.style.set_tb_padding(0.1 * inch)

    t1 = TextRect(0, 0, "42", _text_dict)
    t1.show_debug_rects = True
    t2 = ImageRect(0, 0, "./tests/testfiles/square.png")
    t2.show_debug_rects = True
    t3 = ImageRect(0, 0, "./tests/testfiles/tall.png")
    t3.show_debug_rects = True
    t4 = TextRect(0, 0, "Bottom Text Box", _text_dict)
    t4.show_debug_rects = True

    tl.add_cell("Cell1", t1, constraints=["top left"])
    tl.add_cell("Cell2", t2, constraints=["top left to Cell1 top right"])
    tl.add_cell("Cell3", t3, constraints=["top right"])
    # tl.add_cell("Cell4", t4, constraints=["left to Cell2 left", "below Cell3"])
    tl.add_cell("Cell4", t4, constraints=["top left", "horz_pos 100"])
    tl.show_debug_rects = True

    assert len(tl) == 4
    c = canvas.Canvas(
        "./tests/testfiles/test_layoutcells.pdf", pagesize=(8.5 * inch, 11.0 * inch)
    )
    c.saveState()

    tl.rect.move_top_left_to(Point(1 * inch, 9 * inch))
    tl.draw_in_canvas(c)

    c.showPage()
    c.save()


def test_layoutcell_inside():
    tl = LayoutCell(6 * inch, 1 * inch)
    tl.style.set_with_dict(
        {
            "top-margin": 0.05 * inch,
            "bottom-margin": 0.1 * inch,
            "left-margin": 0.1 * inch,
            "right-margin": 0.05 * inch,
        }
    )
    tl.style.set_tb_padding(0.1 * inch)

    t1 = TextRect(0, 0, "42", _text_dict)
    t1.show_debug_rects = True
    t2 = ImageRect(0, 0, "./tests/testfiles/square.png")
    t2.rotation = -35
    t2.show_debug_rects = True
    t3 = ImageRect(0, 0, "./tests/testfiles/tall.png")
    t3.show_debug_rects = True
    t4 = TextRect(0, 0, "Bottom Text Box", _text_dict)
    t4.show_debug_rects = True

    tl.add_cell("Cell1", t1, constraints=["top left"])
    tl.add_cell("Cell2", t2, constraints=["top left to Cell1 top right"])
    tl.add_cell("Cell3", t3, constraints=["top right"])
    tl.add_cell("Cell4", t4, constraints=["left to Cell2 left", "below Cell3 Cell2"])
    tl.show_debug_rects = True

    tl2 = LayoutCell(6 * inch, 1 * inch)
    tl2.style.set_with_dict(
        {
            "top-margin": 0.05 * inch,
            "bottom-margin": 0.1 * inch,
            "left-margin": 0.1 * inch,
            "right-margin": 0.05 * inch,
        }
    )
    tl2.style.set_tb_padding(0.1 * inch)

    t1 = TextRect(0, 0, "43", _text_dict)
    t1.show_debug_rects = True
    t2 = ImageRect(0, 0, "./tests/testfiles/tall.png")
    t2.show_debug_rects = True
    t3 = ImageRect(0, 0, "./tests/testfiles/long.png")
    t3.show_debug_rects = True
    t4 = TextRect(0, 0, "Another Bottom Text Box", _text_dict)
    t4.rotation = 15
    t4.show_debug_rects = True
    t5 = TextRect(0, 0, "Cell5 Text Box", _text_dict)
    t5.show_debug_rects = True
    t6 = TextRect(0, 0, "Cell6 Text Box", _text_dict)
    t6.show_debug_rects = True

    tl2.add_cell("Cell1", t1, constraints=["top left"])
    tl2.add_cell("Cell2", t2, constraints=["top left to Cell1 top right"])
    tl2.add_cell("Cell3", t3, constraints=["top right"])
    tl2.add_cell("Cell4", t4, constraints=["left to Cell2 left", "below Cell3 Cell2"])
    tl2.add_cell(
        "Cell5",
        t5,
        constraints=[
            "right_of Cell2 Cell4",
            "below Cell1",
            "left to Cell6 right"
            # "right to Cell3 right resize",
        ],
    )
    tl2.add_cell(
        "Cell6",
        t6,
        constraints=[
            "between_horz parent_left and parent_right",
            # "between_horz Cell1 Cell2 and Cell3",
            "between_vert Cell1 and Cell4 parent_bottom",
        ],
    )
    tl2.show_debug_rects = True

    tr = TableColumn(6 * inch, 7 * inch)
    tr.add_row("Row1", tl, height=CONTENT_SIZE)
    tr.add_row("Row2", tl2, height=CONTENT_SIZE)
    tr.show_debug_rects = True
    c = canvas.Canvas(
        "./tests/testfiles/test_layoutcells_inside.pdf",
        pagesize=(8.5 * inch, 11.0 * inch),
    )
    c.saveState()
    tr.rect.move_top_left_to(Point(1 * inch, 9 * inch))
    tr.draw_in_canvas(c)
    assert tl2.has_overlapped_cells()
    assert not tl2.has_clipped_cells()
    # for cell in tl2.iter_cells():
    #     print(cell.label, tl2.is_cell_clipped(cell.label), tl2.is_cell_overlapped(cell.label))
    assert not tl2.is_cell_overlapped("Cell1")
    assert tl2.is_cell_overlapped("Cell5")
    c.showPage()
    c.save()
