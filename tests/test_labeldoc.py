# Sample Test passing with nose and pytest

import random

from reportlab.lib.units import inch
from toolbox import *
from pdfdoc import *

_test_dict = {"left-margin": 1 * inch, "right-margin": 1 * inch, "horz-align": "left"}


def test_labeldoc_init():
    ld = LabelDoc("./testfiles/test_labeldoc.pdf", style=AVERY_5164_LABEL_DOC_STYLE)
    assert ld.nrows == 3
    assert ld.ncolumns == 2
    assert ld.total_rows == 3
    assert ld.total_columns == 3


def test_content_idx():
    ld = LabelDoc("./testfiles/test_labeldoc.pdf", style=AVERY_5164_LABEL_DOC_STYLE)
    rx = [0, 0, 1, 1, 2, 2, 0, 0, 1, 1]
    cx = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    for i, x in enumerate(range(10)):
        r, c = ld.get_row_col(x)
        assert r == rx[i] and c == cx[i]


def test_labeldoc_iter():
    ld = LabelDoc("./testfiles/test_labeldoc.pdf", style=AVERY_5262_LABEL_DOC_STYLE)
    labels = [i for i in range(25)]
    for label in ld.iter_doc(labels):
        tr = TextRect(withText="Label %d" % (label))
        tr.show_debug_rects = True
        ld.add_label(tr)


def test_simple_label():
    ld = LabelDoc("./testfiles/test_simplelabel.pdf", style=AVERY_5267_LABEL_DOC_STYLE)
    labels = [i for i in range(25)]
    for label in ld.iter_doc(labels):
        sl = SimpleLabel(line1="Title %d" % (label), line2="subtitle", line3="subtitle")
        sl.show_debug_rects = True
        ld.add_label(sl)


def test_plaintext_label():
    ld = LabelDoc(
        "./testfiles/test_plaintextlabel.pdf", style=AVERY_5260_LABEL_DOC_STYLE
    )
    labels = [i for i in range(25)]
    WORDS = (
        "python",
        "jumble",
        "easy",
        "difficult",
        "answer",
        "xylophone",
        "125",
        "valid",
        "Up",
        "Down",
        "Left",
        "Right",
        "British",
        "Rail",
        "Transport",
        "Kennedy",
        "Connaught",
        "Kowloon",
        "Bonham Strand",
    )
    for i, label in enumerate(ld.iter_doc(labels)):
        text = ["Label %d`" % (i)]
        others = [random.choice(WORDS) for _ in range(random.randint(1, 12))]
        others.extend(
            [str(random.randint(10, 1024)) for _ in range(random.randint(0, 8))]
        )
        text.extend(others)
        text = " ".join(text)
        sl = PlainTextLabel(text=text)
        sl.textlabel.font = "DIN-Medium"
        sl.textlabel.vert_align = "top"
        sl.show_debug_rects = True
        ld.add_label(sl)


def test_generic_labeldoc():
    ld = LabelDoc(
        "./testfiles/test_generic_label.pdf", style=AVERY_5263_LABEL_DOC_STYLE
    )
    labels = [i for i in range(25)]
    for label in ld.iter_doc(labels):
        rt = random.random()
        if rt > 0.67:
            subtitle = "This is a really long bit of text for the subtitle which is more than one line"
        elif rt < 0.33:
            subtitle = "Subtitle Line"
        else:
            subtitle = None
        rp = random.random()
        if rp > 0.85:
            show_pattern = "slant-line"
        elif rp < 0.15:
            show_pattern = "squares"
        else:
            show_pattern = None
        if random.random() > 0.5:
            colour = random.randint(0, 100)
        else:
            colour = None
        gl = GenericLabel(
            title="Label %d" % (label),
            subtitle=subtitle,
            colour=colour,
            pattern=show_pattern,
        )
        gl.set_debug_rects(True)
        ld.add_label(gl)
