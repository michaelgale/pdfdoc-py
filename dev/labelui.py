import os
import customtkinter as ctk
from rich import inspect, print
from ctkhelpers import *
from pdfdoc import *
from tkinter import font

try:
    import cadquery as cq
    from cqkit import *
except:
    pass

HELP_TEXT = """
Simple Labels:
Title 1`Subtitle 1\nTitle 2`Subtitle 2

LEGO:
3001`0,15,72
4070`71
3024`Tan
3068b`Red`2x Tiles

Safety:
warning_electrical`Danger 240 VAC`Do not touch`30`4
mandatory_icon`Do this thing``30`3

Mechanical:
M6 x 10 mm phillips csk
M6 x 12 socket hex
M2.5 x 10 torx socket
#6-32 x 1-1/2 screw csk flat
#8 x 3/4 wood screw csk phillips
M2 star washer
M2 washer
M5 lock nut
M4 nut
"""

DOC_STYLE_3D_PRINT = {
    "height": 30 * mm,
    "width": 50 * mm,
    "columns": 1,
    "rows": 1,
    "top-margin": 1.5 * mm,
    "bottom-margin": 1.5 * mm,
    "left-margin": 1.5 * mm,
    "right-margin": 1.5 * mm,
    "gutter-width": 0,
    "gutter-height": 0,
}


LABEL_STYLES = {
    "Avery 5260": AVERY_5260_LABEL_DOC_STYLE,
    "Avery 5262": AVERY_5262_LABEL_DOC_STYLE,
    "Avery 5263": AVERY_5263_LABEL_DOC_STYLE,
    "Avery 5267": AVERY_5267_LABEL_DOC_STYLE,
    "Avery 5164": AVERY_5164_LABEL_DOC_STYLE,
    "Avery 35520": AVERY_35520_LABEL_DOC_STYLE,
    "Avery 8126": AVERY_8126_LABEL_DOC_STYLE,
    "Unistat 4262": UNISTAT_4262_LABEL_DOC_STYLE,
    "Unistat 4270": UNISTAT_4270_LABEL_DOC_STYLE,
    "Custom": DOC_STYLE_3D_PRINT,
}
LABEL_FN = "label_sheet.pdf"

DEF_TITLE_FONT = "DIN-Medium"
DEF_TITLE_SZ = 18
DEF_SUBTITLE_FONT = "DIN-Regular"
DEF_SUBTITLE_SZ = 11

TAG_L = 10
TAG_W = 8
TAB_L, TAB_W = 6.5, 8.5
NOTCH_W = 2.5
NOTCH_D = 2.75
SLOT_L, SLOT_W = 3.25, 1.6
SLOT_CTR = 2.5


class LabelStyle:

    def __init__(self, style_name, index, **kwargs):
        self.name = style_name
        self.index = index
        self.style = LABEL_STYLES[style_name]
        self.title_size = None
        self.subtitle_size = None
        if self.style["columns"] < 4:
            self.title_size = 17.5
            self.subtitle_size = 11

    @property
    def description(self):
        return "%s (%d x %d)" % (self.name, self.style["columns"], self.style["rows"])


LABEL_TEMPLATES = [LabelStyle(k, i) for i, k in enumerate(LABEL_STYLES.keys())]


def fraction_symbol(text):
    s = text.replace("1/2", "½")
    s = s.replace("1/4", "¼")
    s = s.replace("3/4", "¾")
    s = s.replace("1/8", "⅛")
    s = s.replace("3/8", "⅜")
    s = s.replace("5/8", "⅝")
    s = s.replace("7/8", "⅞")
    return s


def float_or_none(v):
    try:
        v = float(v)
    except ValueError:
        v = None
    return v


def set_widget_text(widget, text):
    widget.delete("0.0", "end")
    widget.insert(index="0.0", text=text)


def lego_labels(text):
    from brickbom import BOM, BOMPart, BOMLabels
    from ldrawpy import LDRColour

    lines = text.splitlines()
    b = BOM()
    for line in lines:
        ls = line.split("`")
        if len(ls) == 2:
            cs = ls[1].split(",")
            for c in cs:
                try:
                    c = int(c)
                except:
                    c = str(c)
                p = BOMPart(1, ls[0], LDRColour(c))
                b.add_part(p)
        elif len(ls) == 3:
            try:
                c = int(ls[1])
            except:
                c = str(ls[1])
            p = BOMPart(1, ls[0], LDRColour(c))
            p.desc = ls[2]
            p.category = "custom"
            b.add_part(p)
    d1 = BOMLabels(LABEL_FN, b)
    d1.render_pdf()


class StyleItemFrame(ctk.CTkFrame):

    def __init__(self, master, label, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=3)
        self.grid_columnconfigure(4, weight=3)
        self.grid_columnconfigure(5, weight=1)

        self.font_obj = ctk.CTkFont(family="Helvetica", size=20, weight="bold")
        available_fonts = sorted(list(REGISTERED_FONTS))
        self.label = ctk.CTkLabel(master=self, width=80, text=label, anchor="e")
        self.font_choice = ctk.CTkOptionMenu(
            self,
            values=available_fonts,
            command=self.change_font,
            width=184,
        )
        self.font_size = ctk.CTkEntry(self, width=50)
        self.horz_align = LabelledSegmentFrame(
            self, "Horz", ["L", "C", "R"], label_width=32
        )
        self.vert_align = LabelledSegmentFrame(
            self, "Vert", ["T", "C", "B"], label_width=32
        )
        self.fg_colour = LabelledEntryFrame(self, "FG colour")
        self.bg_colour = LabelledEntryFrame(self, "BG colour")
        self.swap_button = ctk.CTkButton(self, 40, text="<>", command=self.swap_colours)

        self.label.grid(row=0, column=0, padx=5, pady=2, sticky="we")
        self.font_choice.grid(row=0, column=1, padx=2, pady=2, sticky="we")
        self.font_size.grid(row=0, column=2, padx=2, pady=2, sticky="we")
        self.horz_align.grid(row=0, column=3, padx=2, pady=2, sticky="we")
        self.vert_align.grid(row=0, column=4, padx=2, pady=2, sticky="we")
        self.fg_colour.grid(row=1, column=0, columnspan=2, padx=2, pady=2, sticky="we")
        self.bg_colour.grid(row=1, column=2, columnspan=2, padx=2, pady=2, sticky="we")
        self.swap_button.grid(row=1, column=4, padx=2, pady=2, sticky="we")
        set_entry_text(self.font_size, text="10")
        self.fg_colour.set_content("#000000")
        self.bg_colour.set_content("#FFFFFF")
        self.horz_align.set_choice("C")
        self.vert_align.set_choice("C")

    def change_font(self, family):
        self.font_obj.configure(family=family)

    def swap_colours(self):
        tmp = self.fg_colour.content()
        self.fg_colour.set_content(self.bg_colour.content())
        self.bg_colour.set_content(tmp)

    def style_dict(self):
        sd = {
            "font": self.font_choice.get(),
            "font-size": float(self.font_size.get()),
            "horz-align": {"L": "left", "C": "centre", "R": "right"}[
                self.horz_align.choice()
            ],
            "vert-align": {"T": "top", "C": "centre", "B": "bottom"}[
                self.vert_align.choice()
            ],
            "font-colour": self.fg_colour.content(),
            "background-colour": self.bg_colour.content(),
        }
        if not self.bg_colour.content() == "#FFFFFF":
            sd["background-fill"] = True
        return sd

    def alignment_str(self):
        xa = {"L": "<X", "C": "X", "R": ">X"}[self.horz_align.choice()]
        ya = {"T": ">Y", "C": "Y", "B": "<Y"}[self.vert_align.choice()]
        return "%s %s >>Z" % (xa, ya)


class StyleFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.title_style = StyleItemFrame(master=self, label="Title font")
        self.subtitle_style = StyleItemFrame(master=self, label="Subtitle font")
        self.title_ratio = LabelledSliderFrame(
            self, "Title size", callback=self.title_ratio_changed, default_val=37
        )
        self.border_line = ctk.CTkCheckBox(self, 180, text="Show borderline")

        self.title_style.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        self.subtitle_style.grid(
            row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w"
        )
        self.title_ratio.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.border_line.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    def title_ratio_changed(self, value):
        self.title_ratio.set_value(value)


class LabelSizeFrame(ctk.CTkFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.label_size = LabelledEntryFrame(self, "Label size (L x W)", "mm")
        self.base_thickness = LabelledEntryFrame(self, "Base thickness", "mm")
        self.text_thickness = LabelledEntryFrame(self, "Text thickness", "mm")
        self.corner_radius = LabelledEntryFrame(self, "Corner radius", "mm")
        self.margin = LabelledEntryFrame(self, "Margin", "mm")
        self.end_tabs = ctk.CTkCheckBox(self, 180, text="Cable tie tabs")

        self.label_size.grid(row=0, column=0, padx=5, pady=2, sticky="nw")
        self.margin.grid(row=0, column=1, padx=5, pady=2, sticky="nw")
        self.base_thickness.grid(row=1, column=0, padx=5, pady=2, sticky="nw")
        self.text_thickness.grid(row=1, column=1, padx=5, pady=2, sticky="nw")
        self.corner_radius.grid(row=2, column=0, padx=5, pady=2, sticky="nw")
        self.end_tabs.grid(row=2, column=1, padx=5, pady=2, sticky="nw")

        self.label_size.set_content("50 x 30")
        self.base_thickness.set_content("0.6")
        self.text_thickness.set_content("0.4")
        self.corner_radius.set_content("1.5")
        self.margin.set_content("1.0")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.cq_obj = None
        self.geometry("1280x800")
        self.title("Label Generator")
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1, minsize=300)
        self.grid_columnconfigure(0, weight=4, minsize=150)
        self.grid_columnconfigure(1, weight=4, minsize=150)
        self.grid_columnconfigure(2, weight=1, minsize=700)

        self.template = RadioButtonFrame(
            self,
            choices=[e.description for e in LABEL_TEMPLATES],
            title="Label Template",
        )
        self.labeltype = RadioButtonFrame(
            self,
            choices=["Simple", "LEGO", "Mechanical", "Safety"],
            title="Label Type",
        )
        self.style_frame = StyleFrame(self)
        self.label_item_list = ctk.CTkTextbox(
            master=self, width=600, height=300, font=("Menlo", 13)
        )
        self.help_text = ctk.CTkTextbox(
            master=self, width=500, height=300, font=("Menlo", 13)
        )
        self.show_outline = ctk.CTkCheckBox(self, text="Show outline")
        self.generate_button = ctk.CTkButton(
            self, text="Generate", command=self.generate_button_callback
        )
        self.label_size_frame = LabelSizeFrame(self)

        self.template.grid(row=0, column=1, rowspan=2, padx=5, pady=2, sticky="new")
        self.labeltype.grid(row=0, column=0, rowspan=2, padx=2, pady=2, sticky="new")
        self.style_frame.grid(row=0, column=2, padx=2, pady=2, sticky="news")
        self.show_outline.grid(row=2, column=0, padx=5, pady=5, sticky="new")
        self.label_size_frame.grid(row=1, column=2, padx=2, pady=2, sticky="new")
        self.generate_button.grid(row=2, column=1, padx=5, pady=5)
        self.label_item_list.grid(
            row=3, column=0, columnspan=2, padx=5, pady=5, sticky="news"
        )
        self.help_text.grid(row=3, column=2, padx=2, pady=5, sticky="news")
        set_widget_text(self.label_item_list, "Title 1`Subtitle 1\nTitle 2`Subtitle 2")
        set_widget_text(self.help_text, HELP_TEXT)

        self.style_frame.title_style.font_choice.set(DEF_TITLE_FONT)
        self.style_frame.subtitle_style.font_choice.set(DEF_SUBTITLE_FONT)
        self.style_frame.title_style.change_font(DEF_TITLE_FONT)
        self.style_frame.subtitle_style.change_font(DEF_SUBTITLE_FONT)
        set_entry_text(self.style_frame.title_style.font_size, str(DEF_TITLE_SZ))
        set_entry_text(self.style_frame.subtitle_style.font_size, str(DEF_SUBTITLE_SZ))

    def generate_button_callback(self):
        label_type = self.labeltype.choice()
        labels = self.label_item_list.get("0.0", "end").splitlines()
        labels = [label for label in labels if len(label) > 1]
        fn = LABEL_FN
        if label_type == 0:
            fn = self.generate_simple_labels(labels)
        if label_type == 1:
            lego_labels(self.label_item_list.get("0.0", "end"))
        if label_type == 2:
            self.generate_mechanical_labels(labels)
        if label_type == 3:
            self.generate_safety_labels(labels)
        # if fn.endswith(".pdf"):
        os.system("open %s" % (fn))

    def generate_safety_labels(self, labels):
        template = LABEL_TEMPLATES[self.template.choice()]
        title_style = self.style_frame.title_style.style_dict()

        ld = LabelDoc(LABEL_FN, style=template.style)
        for label in ld.iter_doc(labels):
            es = label.split("`")
            if len(es) < 3:
                continue
            aspect_ratio = float_or_none(es[4]) if len(es) > 4 else None
            size = float_or_none(es[3]) if len(es) > 3 else None
            sl = SafetyLabel(
                es[0],
                title=es[1],
                description=es[2],
                size=size,
                aspect_ratio=aspect_ratio,
                font=title_style["font"],
                vertical="vertical" in es,
            )
            sl.show_debug_rects = self.show_outline.get()
            ld.add_label(sl)

    def generate_mechanical_labels(self, labels):
        template = LABEL_TEMPLATES[self.template.choice()]
        title_style = self.style_frame.title_style.style_dict()
        subtitle_style = self.style_frame.subtitle_style.style_dict()
        ld = LabelDoc(LABEL_FN, style=template.style)
        for label in ld.iter_doc(labels):
            if len(label) < 2:
                continue
            item = MechanicalItem.from_str(label)
            inspect(item)
            sl = MechanicalLabel(
                item.label_title,
                subtitle=item.description,
                colour=item.colour,
                symbol="../images/%s" % (item.symbol_filename),
            )
            # if template.title_size is not None:
            sl.title.font_size = title_style["font-size"]
            sl.auxtitle.font_size = title_style["font-size"]
            sl.subtitle.font_size = subtitle_style["font-size"]
            sl.title.style["font-name"] = title_style["font"]
            sl.auxtitle.style["font-name"] = title_style["font"]
            sl.subtitle.style["font-name"] = subtitle_style["font"]
            sl.subtitle.top_padding = 4
            sl.subtitle.vert_align = "top"
            sl.subtitle.left_padding = 0
            sl.show_debug_rects = self.show_outline.get()
            ld.add_label(sl)

    def generate_simple_labels(self, labels):
        template = LABEL_TEMPLATES[self.template.choice()]
        title_style = self.style_frame.title_style.style_dict()
        subtitle_style = self.style_frame.subtitle_style.style_dict()
        title_ratio = self.style_frame.title_ratio.value() / 100

        if self.template.choice() == len(LABEL_TEMPLATES) - 1:
            sz = self.label_size_frame.label_size.content()
            sz = sz.replace("x", " ")
            sz = sz.split()
            xl, yl = float(sz[0]), float(sz[1])
            xi = xl - 2 * float(self.label_size_frame.margin.content())
            yi = yl - 2 * float(self.label_size_frame.margin.content())
            hb = float(self.label_size_frame.base_thickness.content())
            ht = float(self.label_size_frame.text_thickness.content())
            cr = float(self.label_size_frame.corner_radius.content())
            _, title_font_path = find_font(title_style["font"])
            font_size = PTS2MM(title_style["font-size"])
            line_width = font_size / 10
            _, subtitle_font_path = find_font(subtitle_style["font"])
            sub_font_size = PTS2MM(subtitle_style["font-size"])
            solids = []
            for label in labels:
                ls = label.split("`")
                rb = box(xl, yl, hb, cr)
                if self.label_size_frame.end_tabs.get():
                    xt = TAB_L + NOTCH_W
                    rt = box(xt, TAB_W, hb, 0.8)
                    rb = rb.union(rt.translate((-xl / 2 - xt / 2, 0, 0)))
                    rb = rb.union(rt.translate((xl / 2 + xt / 2, 0, 0)))
                    rs = cq.Workplane().slot2D(2 * NOTCH_D, NOTCH_W, 90).extrude(hb)
                    for pt in rect_corners((xl / 2 + NOTCH_W / 2), (TAG_W / 2), 0):
                        rb = rb.cut(rs.translate(pt))
                    rs = box(SLOT_L, SLOT_W, hb, edge_radius=0.25)
                    for pt in rect_corners((xl / 2 + NOTCH_W + TAB_L / 2), SLOT_CTR, 0):
                        rb = rb.cut(rs.translate(pt))
                    rb = (
                        rb.edges("|Z")
                        .edges(
                            HasXCoordinateSelector(
                                [-xl / 2 - NOTCH_W, xl / 2 + NOTCH_W]
                            )
                        )
                        .fillet(0.8)
                    )

                rt1 = cq.Workplane().text(
                    ls[0], font_size, ht, fontPath=title_font_path
                )
                if len(ls) > 1:
                    rt2 = cq.Workplane().text(
                        ls[1], sub_font_size, ht, fontPath=subtitle_font_path
                    )
                if len(ls) > 2:
                    rt3 = cq.Workplane().text(
                        ls[2], sub_font_size, ht, fontPath=subtitle_font_path
                    )
                if len(ls) == 1:
                    rt1 = realign(
                        rt1,
                        box(xi, yi, hb),
                        self.style_frame.title_style.alignment_str(),
                    )
                    r = rb.union(rt1)
                if len(ls) == 2:
                    yl1 = yi * title_ratio
                    yl2 = yi * (1 - title_ratio)
                    rtop = box(xi, yl1, hb).translate((0, yi / 2 - yl1 / 2, 0))
                    rbot = box(xi, yl2, hb).translate((0, -yi / 2 + yl2 / 2, 0))
                    rt1 = realign(
                        rt1, rtop, self.style_frame.title_style.alignment_str()
                    )
                    rt2 = realign(
                        rt2, rbot, self.style_frame.subtitle_style.alignment_str()
                    )
                    r = rb.union(rt1).union(rt2)
                if len(ls) == 3:
                    yl1 = yi * title_ratio
                    yl2 = yi * (1 - title_ratio) / 2
                    rtop = box(xi, yl1, hb).translate((0, yi / 2 - yl1 / 2, 0))
                    rbot1 = box(xi, yl2, hb).translate((0, -yi / 2 + 1.5 * yl2, 0))
                    rbot2 = box(xi, yl2, hb).translate((0, -yi / 2 + yl2 / 2, 0))
                    rt1 = realign(
                        rt1, rtop, self.style_frame.title_style.alignment_str()
                    )
                    rt2 = realign(
                        rt2, rbot1, self.style_frame.subtitle_style.alignment_str()
                    )
                    rt3 = realign(
                        rt3, rbot2, self.style_frame.subtitle_style.alignment_str()
                    )
                    r = rb.union(rt1).union(rt2).union(rt3)
                if len(ls) >= 2:
                    if self.style_frame.border_line.get():
                        yl1 = yi * title_ratio
                        rl = box(xi, line_width, ht)
                        r = r.union(rl.translate((0, yi / 2 - yl1, hb)))

                solids.append(r)
            bounds = box(200, 200, hb + ht)
            ly = GridLayoutArranger(solids, bounds=bounds)
            ly.x_padding = 5
            ly.y_padding = 5
            self.cq_obj = ly.layout(rowwise=True, as_compound=True)
            FN = LABEL_FN.replace(".pdf", ".step")
            export_step_file(self.cq_obj, FN)
            return FN

        ld = LabelDoc(LABEL_FN, style=template.style)
        for label in ld.iter_doc(labels):
            tst = label.split("`")
            sl = SimpleLabel(line1=tst[0])
            sl.title.style.set_with_dict(title_style)
            sl.title.horz_align = title_style["horz-align"]
            sl.title.font_size = title_style["font-size"]
            sl.title.style["border-line-bottom"] = self.style_frame.border_line.get()
            sl.title.style["border-width"] = title_style["font-size"] / 10
            sl.line2.style.set_with_dict(subtitle_style)
            sl.line2.horz_align = subtitle_style["horz-align"]
            sl.line2.font_size = subtitle_style["font-size"]
            sl.line2.top_padding = 2
            sl.textcol.set_cell_visible("Line2", False)
            sl.textcol.set_cell_visible("Line3", False)
            if len(tst) > 1:
                sl.line2.text = tst[1]
                sl.line2.style.set_with_dict(subtitle_style)
                sl.line2.horz_align = subtitle_style["horz-align"]
                sl.line2.font_size = subtitle_style["font-size"]
                sl.textcol.set_cell_visible("Line2", True)
            if len(tst) > 2:
                sl.line3.text = tst[2]
                sl.line3.style.set_with_dict(subtitle_style)
                sl.line3.horz_align = subtitle_style["horz-align"]
                sl.line3.font_size = subtitle_style["font-size"]
                sl.textcol.set_cell_visible("Line3", True)
            if len(tst) == 1:
                sl.textcol.set_row_height("Title", 1)
            sl.textcol.set_row_height("Title", title_ratio)
            # print(sl.title.style)
            sl.show_debug_rects = self.show_outline.get()
            ld.add_label(sl)
        return LABEL_FN


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()

"""
M6 x 10 mm phillips csk
M6 x 12 socket hex
M2.5 x 10 torx socket
M1.6 x 8 T6 torx CSK
#6 x 1-1/2 wood screw csk robertson
#8 x 3/4 wood screw csk phillips
#6-32 x 1/2 csk robertson #1
#4-40 x 3/4 flat head flat
M2 star washer
M2 washer
M5 lock nut
M4 nut

0603R`560 Ω
0603R`4.7 kΩ
0603R`10 kΩ

0805R`100 Ω
0805R`200 Ω
0805R`220 Ω
0805R`470 Ω
0805R`4.7 kΩ
0805R`9.1 kΩ
0805R`47 kΩ
0805R`100 kΩ

0603C`0.1 μF 50V
0805C`0.1 μF 50V
0805C`0.01 μF
0805C`0.047 μF

1206`Yellow LED
SN74LVC541`IC Buffer 20-SOP

"""
