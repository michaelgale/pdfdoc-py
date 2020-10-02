# Sample Test passing with nose and pytest

import os
import sys
import pytest
import math
import random
import pprint
from reportlab.lib.units import inch, mm
from toolbox import *
from ldrawpy import LDRColour
from pdfdoc import *


def test_document_init():
    doc = Document("test_document.pdf")
    assert doc.filename == "test_document.pdf"
    doc.set_page_size(PAGE_A4)
    r = doc.page_rect
    assert r.left == 0
    assert r.top == 297 * mm
    assert r.right == 210 * mm
    assert r.bottom == 0
    doc.set_page_size(PAGE_A4, orientation="landscape")
    r = doc.page_rect
    assert r.left == 0
    assert r.right == 297 * mm
    assert r.top == 210 * mm
    assert r.bottom == 0

class DocStartCallback(DocumentCallback):
    
    def __init__(self):
        super().__init__()
        self.style = {
            "font-size": 14,
            "font-colour": LDRColour.RGBFromHex("#000000"),
            "horz-align": "centre",
            "vert-align": "centre",
        }        

    def render(self, context):
        tr = TextRect(5*inch, 1*inch, "Document Start", style=self.style)
        r = context["inset_rect"]
        tr.rect = r
        tr.show_debug_rects = True
        tr.draw_in_canvas(context["canvas"])

class PageStartCallback(DocumentCallback):
    def __init__(self):
        super().__init__()
        self.style = {
            "background-fill": True,
            "background-colour": LDRColour.RGBFromHex("#FFFFBE"),
        }

    def render(self, context):
        r = context["page_rect"]
        cr = ContentRect(r.width, r.height)
        cr.rect = r
        cr.style.set_with_dict(self.style)
        cr.draw_in_canvas(context["canvas"])


class PageEndCallback(DocumentCallback):
    def __init__(self):
        super().__init__()
        self.style = {
            "font-size": 14,
            "font-colour": LDRColour.RGBFromHex("#000000"),
            "horz-align": "right",
            "vert-align": "top",
        }

    def render(self, context):
        r = context["footer_rect"]
        tr = TextRect(r.width, r.height, str(context["page_number"]), style=self.style)
        tr.rect = r
        tr.show_debug_rects = True
        tr.draw_in_canvas(context["canvas"])        
      
class DocEndCallback(DocumentCallback):
    
    def __init__(self):
        super().__init__()
        self.style = {
            "font-size": 14,
            "font-colour": LDRColour.RGBFromHex("#000000"),
            "horz-align": "centre",
            "vert-align": "centre",
        }

    def render(self, context):
        r = context["inset_rect"]
        tr = TextRect(r.width, r.height, "Document End", style=self.style)
        tr.rect.move_top_left_to(r.get_top_left())
        tr.show_debug_rects = True
        tr.draw_in_canvas(context["canvas"])

def test_document_callbacks():
    doc = Document("./testfiles/test_document.pdf")
    assert doc.filename == "./testfiles/test_document.pdf"
    doc.set_page_size(PAGE_LETTER, with_bleed=8 * mm)
    ds = DocStartCallback()
    ds.z_order = 1
    doc.doc_start_callbacks = [ds]
    doc.doc_end_callbacks = DocEndCallback()
    doc.page_start_callbacks = PageStartCallback()
    page_num_callback = PageNumberCallback()
    page_num_callback.show_in_header = True
    page_num_callback.show_in_footer = False
    page_num_callback.alternate_odd_even = True
    page_num_callback.page_exclusions = [1, 5]
    doc.page_end_callbacks = [PageEndCallback(), page_num_callback]
    for section, ctx in doc.iter_doc([1, 2, 3, 4]):
        doc.page_break()

def test_document_cropmarks():
    doc = Document("./testfiles/test_cropmarks.pdf")
    doc.set_page_size(PAGE_A5, orientation="landscape", with_bleed=10 * mm)
    crops = CropMarksCallback(length=5 * mm)
    back = PageBackgroundCallback(colour=(0.7, 0.8, 1.0))
    crosses = CropMarksCallback(length=3 * mm)
    crosses.show_cross_hairs = True
    crosses.show_as_corners = False
    crosses.style.set_attr("line-width", 0.25 * mm)
    crosses.style.set_attr("line-colour", (1, 0, 0))
    doc.page_end_callbacks = [crops, crosses]
    doc.page_start_callbacks = back
    for section, ctx in doc.iter_doc([1, 2, 3]):
        doc.page_break()

def test_document_sections():
    doc = Document("./testfiles/test_sections.pdf")
    doc.set_page_size(PAGE_LETTER)
    doc.section_list = ["Title", "Middle", "End"]

    back1 = PageBackgroundCallback(colour=(1.0, 0.8, 0.8))
    back1.sections_active = ["Title"]
    back2 = PageBackgroundCallback(colour=(0.8, 1.0, 0.8))
    back2.sections_active = ["Middle"]
    back3 = PageBackgroundCallback(colour=(0.8, 0.8, 1.0))
    back3.sections_active = ["End"]
    p1 = PageNumberCallback(show_in_header=True)
    p1.section_exclusions = ["Title"]
    p2 = PageNumberCallback(show_in_footer=True, number_format="roman-lowercase")
    p2.set_style({"horz-align": "right"})
    p2.sections_active = ["Title"]
    dc = DocEndCallback()
    dc.section_exclusions = ["Title", "Middle"]

    doc.page_start_callbacks = [back1, back2, back3, dc]
    doc.page_end_callbacks = [p1, p2]
    for section, ctx in doc.iter_doc(range(1, 4)):
        doc.section_break(new_section="Title", new_page_number=1)
        doc.page_break()
        doc.page_break()
        doc.section_break(new_section="Middle", new_page_number=1)
        doc.page_break()
        doc.page_break()
        doc.section_break(new_section="End")
        doc.page_break()

def test_document_columns():
    doc = Document("./testfiles/test_columns.pdf")
    doc.set_page_size(PAGE_LETTER)
    doc.style["gutter-width"] = 0.5 * inch
    doc.set_columns(2)
    r1 = doc.column_rects[0]
    r2 = doc.column_rects[1]
    g1 = doc.gutter_rects[0]
    assert len(doc.column_rects) == 2
    assert len(doc.gutter_rects) == 1
    assert r1.left == 36
    assert r1.right == 288
    assert r2.left == 324
    assert r2.right == 576
    assert g1.left == 288
    assert g1.right == 324
    p1 = PageNumberCallback(show_in_footer=True)
    doc.page_end_callbacks = [p1]
    cl = ColumnLineCallback(style={
        "top-margin": 0.25 * inch,
        "bottom-margin": 0.25 * inch,
        "line-width": 0.05 * inch,
        "line-colour": (0, 0.4, 0.8),
    })
    doc.column_end_callbacks = [cl]
    doc._doc_start()
    for x in range(20):
        doc.cursor_auto_shift(200)
        # print("Page: %d Column: %d Cursor: %.1f,%.1f" % (doc.page_number, doc.column, doc.cursor[0], doc.cursor[1]))
    doc.end_document()
