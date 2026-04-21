# pdfdoc-py

![python version](https://img.shields.io/static/v1?label=python&message=3.6%2B&color=blue&style=flat&logo=python)
![https://github.com/michaelgale/pdfdoc-py/blob/master/LICENSE](https://img.shields.io/badge/license-MIT-blue.svg)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

**pdfdoc-py** is a Python library for compositing and generating PDF documents using [reportlab](https://www.reportlab.com/) as the rendering backend. It provides a high-level layout system built around rectangular content regions, a flexible style system, and ready-made document types for label sheets, safety labels, and mechanical part labels.

## Installation

```shell
git clone https://github.com/michaelgale/pdfdoc-py.git
cd pdfdoc-py
python setup.py install
```

After installation:

```python
import pdfdoc
print(pdfdoc.__version__)
```

## Dependencies

- Python 3.6+
- [reportlab](https://pypi.org/project/reportlab/) — PDF rendering engine
- [toolbox-py](https://github.com/michaelgale/toolbox-py) — utility helpers
- [qrcode](https://pypi.org/project/qrcode/) — QR code generation (optional, for `QRCodeRect`)
- [Pillow](https://pypi.org/project/Pillow/) — image handling

## Key Concepts

### Content Rectangles

All visual elements are subclasses of `ContentRect`. Each rect has a size, a `DocStyle` that controls its appearance, and a `draw_in_canvas(c)` method that renders it onto a reportlab canvas.

### DocStyle

A `DocStyle` is a dictionary-backed style object that controls font, colour, margins, padding, borders, alignment, and background for any content rect or table cell. Styles can be passed as plain dicts.

```python
style = {
    "font-name": "Helvetica",
    "font-size": 12,
    "font-colour": (0, 0, 0),
    "background-fill": True,
    "background-colour": (0.9, 0.9, 0.9),
    "left-margin": MM2PTS(3),
    "right-margin": MM2PTS(3),
    "border-outline": True,
    "border-colour": (0, 0, 0),
    "border-width": 0.5,
    "horz-align": "centre",
    "vert-align": "centre",
}
```

### Unit Conversions

```python
from pdfdoc import MM2PTS, IN2PTS, PTS2MM, PTS2IN, PIX2PTS, PTS2PIX

MM2PTS(50)               # 50 mm → points
IN2PTS(2.5)              # 2.5 inches → points
PTS2MM(142.0)            # points → mm
PIX2PTS(800, dpi=300)    # pixels → points at 300 DPI
```

---

## Content Rectangles

### TextRect

Renders a string with configurable font, alignment, clipping, and auto-sizing.

```python
from pdfdoc import *

tr = TextRect(MM2PTS(60), MM2PTS(15), withText="Hello World")
tr.style.set_with_dict({
    "font-name": "Helvetica-Bold",
    "font-size": 14,
    "horz-align": "left",
    "vert-align": "centre",
    "left-margin": MM2PTS(2),
})
```

`shrink_to_fit=True` automatically reduces the font size until the text fits the rect width. `split_lines=True` wraps text across multiple lines.

```python
tr = TextRect(MM2PTS(40), MM2PTS(20), withText="Long text that wraps")
tr.split_lines = True
```

### ImageRect

Embeds a raster image, optionally auto-sizing to its natural dimensions at a given DPI.

```python
img = ImageRect(MM2PTS(50), MM2PTS(30), filename="photo.png")

# Auto-size to natural image dimensions at 150 DPI
img = ImageRect(filename="diagram.png", auto_size=True, dpi=150)
```

Built-in preset graphics (mechanical fastener illustrations, etc.) are available:

```python
img = ImageRect.from_preset("MSPanPhillips")
print(ImageRect.list_presets())
```

### QRCodeRect

Generates a QR code from a string or URL.

```python
qr = QRCodeRect(MM2PTS(30), MM2PTS(30), qrtext="https://example.com")
qr.format = "svg"       # "svg" (default) or "pil"
qr.dot_type = "circle"  # "square" (default) or "circle"
```

Generate a WiFi connection QR code:

```python
qr = QRCodeRect.for_wifi(
    ssid="MyNetwork",
    password="secret123",
    security="WPA",
    hidden=False,
    w=MM2PTS(40),
    h=MM2PTS(40),
)
```

### PatternRect

Fills a rectangle with a repeating pattern (e.g. diagonal hatching).

```python
pr = PatternRect(MM2PTS(60), MM2PTS(30), pattern="slant-line")
pr.foreground_colour = (0, 0, 0)
pr.background_colour = (1, 1, 0.8)
```

### SvgRect

Renders an SVG file into a rectangle.

```python
svg = SvgRect(MM2PTS(50), MM2PTS(50), filename="icon.svg")
svg = SvgRect.from_preset("some_preset")
```

---

## Table Layouts

Tables compose multiple `ContentRect` objects into rows, columns, or grids.

### TableRow / TableColumn

```python
row = TableRow(MM2PTS(150), MM2PTS(20))
row.add_column("label",  TextRect(withText="Part"),        width=MM2PTS(50))
row.add_column("qty",    TextRect(withText="Qty"),         width=MM2PTS(25))
row.add_column("price",  TextRect(withText="Unit Price"),  width=MM2PTS(40))
row.draw_in_canvas(canvas)

col = TableColumn(MM2PTS(60), MM2PTS(80))
col.add_row("title", TextRect(withText="Title"),      height=MM2PTS(20))
col.add_row("body",  TextRect(withText="Body text"),  height=MM2PTS(60))
col.draw_in_canvas(canvas)
```

### TableGrid

A 2-D grid that auto-wraps cells row-wise or column-wise.

```python
grid = TableGrid(MM2PTS(200), MM2PTS(150))
grid.fill_dir = "row-wise"
for i in range(12):
    grid.add_content(TextRect(withText=f"Cell {i}"))
grid.compute_cell_sizes()
grid.draw_in_canvas(canvas)
```

### Create a TableVector from a nested list

```python
data = [
    [TextRect(withText="A"), TextRect(withText="B")],
    [TextRect(withText="C"), TextRect(withText="D")],
]
table = TableVector.from_array(data, fit_to_contents=True)
```

---

## Label Sheet Documents

`LabelDoc` lays out content onto self-adhesive label sheets using pre-defined Avery or Unistat templates.

```python
from pdfdoc import *

ld = LabelDoc("labels.pdf", style=AVERY_5262_LABEL_DOC_STYLE)

items = ["Apple", "Banana", "Cherry", "Date"]
for label, row, col in ld.iter_label(items):
    tr = TextRect(withText=label)
    ld.set_table_cell(tr, row, col)

ld.write()
```

Available label sheet styles:

| Constant | Format | Labels/sheet |
|---|---|---|
| `AVERY_5260_LABEL_DOC_STYLE` | 1" × 2⅝" | 30 |
| `AVERY_5262_LABEL_DOC_STYLE` | 1⅓" × 4" | 14 |
| `AVERY_5263_LABEL_DOC_STYLE` | 2" × 4" | 10 |
| `AVERY_5267_LABEL_DOC_STYLE` | ½" × 1¾" | 80 |
| `AVERY_5164_LABEL_DOC_STYLE` | 3⅓" × 4" | 6 |
| `AVERY_8126_LABEL_DOC_STYLE` | 4" × 6" | 2 |
| `UNISTAT_4262_LABEL_DOC_STYLE` | — | 24 |
| `UNISTAT_4270_LABEL_DOC_STYLE` | — | 65 |

---

## Specialised Label Types

### SafetyLabel

Generates ISO-style safety labels with a hazard icon, title, and optional description. The background colour is automatically selected based on the icon category.

```python
label = SafetyLabel(
    icon="warning_electrical",   # yellow triangle — caution
    title="High Voltage 240 V",
    description="Disconnect power before servicing.",
    width=MM2PTS(80),
)

label = SafetyLabel(
    icon="mandatory_eye_protection",  # blue circle — mandatory
    title="Eye Protection Required",
    width=MM2PTS(60),
    vertical=True,
)

label = SafetyLabel(
    icon="prohibited_no_smoking",  # red circle — prohibition
    title="No Smoking",
    width=MM2PTS(50),
)
```

Icon name prefixes and their colour coding:

| Prefix | Colour | Category |
|---|---|---|
| `warning_*` | Yellow | Caution / hazard |
| `mandatory_*` | Blue | Required PPE / action |
| `prohibited_*` | Red | Prohibition |
| `icon_first_aid` | Green | First aid |
| `icon_info` | White/blue | Information |

### MechanicalLabel

Generates colour-coded labels for mechanical fasteners and hardware.

```python
label = MechanicalLabel(
    title="M3 × 8 mm",
    subtitle="Pan Phillips",
    colour=(0.2, 0.6, 1.0),
    symbol="MSPanPhillips",
)
```

Use `MechanicalItem` to auto-derive label properties from fastener specifications:

```python
item = MechanicalItem(type="MS", metric=True, head="Pan", drive="Phillips",
                      size=3, length=8, units="mm")
label = MechanicalLabel(
    title=item.label_title,
    colour=item.colour,
    symbol=item.symbol,
)
```

### SimpleLabel

A compact three-line text label.

```python
label = SimpleLabel(
    line1="Widget Pro",
    line2="SKU: WGT-42",
    line3="Qty: 10",
)
```

---

## Multi-page Documents

`Document` manages page layout, margins, headers, footers, and page-event callbacks.

```python
from pdfdoc import *
from reportlab.lib.units import inch

doc = Document("report.pdf")
doc.set_page_size(PAGE_A4)
doc.set_margins(
    top=0.75 * inch,
    bottom=0.75 * inch,
    left=inch,
    right=inch,
)
# Attach page-start/page-end callbacks to draw headers/footers, then render.
doc.write()
```

Available page size constants: `PAGE_A3`, `PAGE_A4`, `PAGE_A5`, `PAGE_LETTER`, `PAGE_TABLOID`, `PAGE_LEDGER`, `PAGE_BOOKLET` — each with corresponding `CANVAS_*` tuples for portrait and landscape.

---

## Fonts and Symbols

### Registering Fonts

```python
register_font("MyFont", "/path/to/MyFont.ttf")
register_font_family("/path/to/fonts/")
print(get_system_font_list())
```

### FontAwesome Icons

```python
tr = TextRect(MM2PTS(10), MM2PTS(10))
tr.text = fa_symbol("star")
tr.style.set_with_dict({"font-name": "FontAwesome", "font-size": 20})
```

### Hazard / Safety Symbols

```python
tr = TextRect(MM2PTS(20), MM2PTS(20))
tr.text = haz_symbol("warning_electrical")
tr.style.set_with_dict({"font-name": "Hazard", "font-size": 48})

# Or use the convenience method on TextRect:
tr.set_icon("warning_laser")
```

Available hazard symbol groups: `warning_*` (caution triangles), `mandatory_*` / `prohibited_*` (PPE and prohibition circles), `icon_first_aid`, `icon_info`, `icon_exit`, and directional arrows.

---

## Graphics Utilities

### StyledLine and ArrowHead

```python
line = StyledLine()
line.style.set_with_dict({"stroke-width": 1.5, "stroke-colour": (0, 0, 0)})
line.draw_from_coords(canvas, coords=[(x0, y0), (x1, y1)], arrow1=True)

arrow = ArrowHead()
arrow.draw_in_canvas(canvas, pt=(x, y), dir=0)  # dir: 0=right, 90=up, etc.
```

### Colour Helpers

```python
rl_colour((0.2, 0.5, 0.8))               # RGB tuple → reportlab Color
rl_colour_hex("#FF6600")                  # hex string → reportlab Color
rl_colour_trans((0, 0, 0), alpha=0.4)    # with transparency
```

### PDF Post-processing

```python
convert_pdf_to_png("output.pdf", dpi=150)
convert_pdf_to_thumbnail("output.pdf", width=200)
```

---

## Authors

`pdfdoc-py` was written by [Michael Gale](https://github.com/michaelgale).
