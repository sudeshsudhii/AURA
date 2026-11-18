"""Helpers that build the report on top of the SRMIST template (python-docx).
Formatting follows the template's specification: Times New Roman; chapter headings 16 pt bold, section headings
14 pt bold, sub-section headings 12 pt bold, body 12 pt; 1.5 line spacing; margins L 1.5", R/T/B 1.0"."""
import copy, re
from docx import Document
from docx.shared import Pt, Inches, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING, WD_COLOR_INDEX
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FONT = "Times New Roman"
TEXT_W = 5.77  # inches between margins


def set_font(run, size=None, bold=None, italic=None, name=FONT, color=None, mono=False):
    nm = "Courier New" if mono else name
    run.font.name = nm
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.insert(0, rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(a), nm)
    if size: run.font.size = Pt(size)
    if bold is not None: run.font.bold = bold
    if italic is not None: run.font.italic = italic
    if color: run.font.color.rgb = RGBColor.from_string(color)


def shade(el_pr, fill):
    shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), fill)
    el_pr.append(shd)


def set_col_widths(t, widths):
    """Apply widths (inches) to tblGrid, tblW and every cell so Word and LibreOffice agree."""
    tbl = t._tbl; tblPr = tbl.tblPr
    grid = tbl.find(qn("w:tblGrid"))
    for gc, w in zip(grid.findall(qn("w:gridCol")), widths): gc.set(qn("w:w"), str(int(w * 1440)))
    old = tblPr.find(qn("w:tblW"))
    if old is not None: tblPr.remove(old)
    tw = OxmlElement("w:tblW"); tw.set(qn("w:w"), str(int(sum(widths) * 1440))); tw.set(qn("w:type"), "dxa"); tblPr.append(tw)
    if tblPr.find(qn("w:tblLayout")) is None:
        lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); tblPr.append(lay)
    for row in t.rows:
        for c, w in zip(row.cells, widths): c.width = Inches(w)


class Report:
    def __init__(self, template):
        self.doc = Document(template)
        self.fig_no = {}; self.tab_no = {}
        self.captions = {"fig": [], "tab": []}   # (label, title) in order
        self.refs = []
        self._style_setup()

    # ------------------------------------------------------------------ styles
    def _style_setup(self):
        st = self.doc.styles
        n = st["Normal"]; n.font.name = FONT; n.font.size = Pt(12)
        rf = n.element.get_or_add_rPr().find(qn("w:rFonts"))
        if rf is None:
            rf = OxmlElement("w:rFonts"); n.element.get_or_add_rPr().insert(0, rf)
        for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rf.set(qn(a), FONT)
        for name, size in (("Heading 1", 16), ("Heading 2", 14), ("Heading 3", 12)):
            s = st[name]; s.font.name = FONT; s.font.size = Pt(size); s.font.bold = True; s.font.italic = False
            s.font.color.rgb = RGBColor(0, 0, 0)
            r = s.element.get_or_add_rPr(); rf = r.find(qn("w:rFonts"))
            if rf is None:
                rf = OxmlElement("w:rFonts"); r.insert(0, rf)
            for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
                rf.set(qn(a), FONT)
            for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
                if rf.get(qn(a)) is not None: del rf.attrib[qn(a)]
            pf = s.paragraph_format; pf.keep_with_next = True; pf.space_before = Pt(14 if name != "Heading 3" else 10); pf.space_after = Pt(6)
            pf.line_spacing = 1.15
            pf.left_indent = Inches(0); pf.first_line_indent = Inches(0)

    # ------------------------------------------------------------------ paragraph primitives
    @property
    def body(self): return self.doc.element.body

    def _fmt(self, p, align=None, spacing=1.5, after=6, before=0, keep_next=False, indent=None, first=None, keep_lines=False):
        pf = p.paragraph_format
        pf.line_spacing = spacing; pf.space_after = Pt(after); pf.space_before = Pt(before)
        if align is not None: p.alignment = align
        if keep_next: pf.keep_with_next = True
        if keep_lines: pf.keep_together = True
        if indent is not None: pf.left_indent = Inches(indent)
        if first is not None: pf.first_line_indent = Inches(first)

    TOK = re.compile(r"(\[\[.+?\]\]|\*\*.+?\*\*|\*.+?\*|`.+?`)")

    def runs(self, p, text, size=12, bold=False, italic=False, color=None):
        for part in self.TOK.split(text):
            if not part: continue
            if part.startswith("[["):
                r = p.add_run(part[2:-2]); set_font(r, size, bold, italic); r.font.highlight_color = WD_COLOR_INDEX.YELLOW
            elif part.startswith("**"): r = p.add_run(part[2:-2]); set_font(r, size, True, italic, color=color)
            elif part.startswith("`"): r = p.add_run(part[1:-1]); set_font(r, size, bold, True)   # inline commands: italic serif keeps justified lines even
            elif part.startswith("*"): r = p.add_run(part[1:-1]); set_font(r, size, bold, True, color=color)
            else: r = p.add_run(part); set_font(r, size, bold, italic, color=color)

    def P(self, text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, after=6, first=0.0, **kw):
        p = self.doc.add_paragraph(); self._fmt(p, align, 1.5, after, first=first, **kw)
        self.runs(p, text, size); return p

    def center(self, text, size=12, bold=False, after=6, spacing=1.15, italic=False):
        p = self.doc.add_paragraph(); self._fmt(p, WD_ALIGN_PARAGRAPH.CENTER, spacing, after)
        self.runs(p, text, size, bold, italic); return p

    def pagebreak(self):
        p = self.doc.add_paragraph(); p.add_run().add_break(WD_BREAK.PAGE); self._fmt(p, spacing=1.0, after=0)

    def H1(self, text, break_before=True):
        p = self.doc.add_paragraph(style="Heading 1"); p.paragraph_format.page_break_before = break_before
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(text); set_font(r, 16, True, color="000000"); return p

    def H2(self, text):
        p = self.doc.add_paragraph(style="Heading 2"); r = p.add_run(text); set_font(r, 14, True, color="000000"); return p

    def H3(self, text):
        p = self.doc.add_paragraph(style="Heading 3"); r = p.add_run(text); set_font(r, 12, True, color="000000"); return p

    def plain_title(self, text, size=14, after=12, page_break=True):
        p = self.doc.add_paragraph(); self._fmt(p, WD_ALIGN_PARAGRAPH.CENTER, 1.15, after, keep_next=True)
        if page_break: p.paragraph_format.page_break_before = True
        r = p.add_run(text); set_font(r, size, True); return p

    def bullets(self, items, size=12):
        for it in items:
            p = self.doc.add_paragraph(style="List Bullet")
            self._fmt(p, WD_ALIGN_PARAGRAPH.JUSTIFY, 1.5, 3, indent=0.5, first=-0.25)
            self.runs(p, it, size)

    def numbered(self, items, size=12):
        for i, it in enumerate(items, 1):
            p = self.doc.add_paragraph(); self._fmt(p, WD_ALIGN_PARAGRAPH.JUSTIFY, 1.5, 3, indent=0.5, first=-0.3)
            p.paragraph_format.tab_stops.add_tab_stop(Inches(0.5))
            self.runs(p, f"{i}.\t" + it, size)

    # ------------------------------------------------------------------ code
    def code(self, text, size=8.5, caption=None):
        lines = text.rstrip("\n").split("\n")
        mx = int(5.55*72/(size*0.6))
        for ln in lines:
            if len(ln) > mx: print(f"WARN code line {len(ln)}>{mx}: {ln[:50]}")
        for i, ln in enumerate(lines):
            p = self.doc.add_paragraph(); pf = p.paragraph_format
            pf.line_spacing = 1.0; pf.space_after = Pt(0); pf.space_before = Pt(0)
            pf.left_indent = Inches(0.1); pf.right_indent = Inches(0.1)
            pf.keep_together = True
            if i < len(lines) - 1: pf.keep_with_next = True
            ppr = p._p.get_or_add_pPr(); shade(ppr, "F2F2F2")
            r = p.add_run(ln if ln else " "); set_font(r, size, mono=True)
        sp = self.doc.add_paragraph(); self._fmt(sp, spacing=1.0, after=4)

    # ------------------------------------------------------------------ figures and tables
    def FIG(self, ch, filename, caption, width=5.6):
        n = self.fig_no.get(ch, 0) + 1; self.fig_no[ch] = n
        label = f"Fig. {ch}.{n}"
        p = self.doc.add_paragraph(); self._fmt(p, WD_ALIGN_PARAGRAPH.CENTER, 1.0, 3, before=6, keep_next=True)
        p.add_run().add_picture(f"../figures/{filename}", width=Inches(width))
        c = self.doc.add_paragraph(); self._fmt(c, WD_ALIGN_PARAGRAPH.CENTER, 1.15, 10)
        r = c.add_run(f"{label}: {caption}"); set_font(r, 11, True)
        self.captions["fig"].append((f"{ch}.{n}", caption)); return label

    def TABLE(self, ch, caption, header, rows, widths, size=10, align=None, bold_first_col=False, note=None):
        n = self.tab_no.get(ch, 0) + 1; self.tab_no[ch] = n
        c = self.doc.add_paragraph(); self._fmt(c, WD_ALIGN_PARAGRAPH.CENTER, 1.15, 4, before=6, keep_next=True)
        r = c.add_run(f"Table {ch}.{n}: {caption}"); set_font(r, 11, True)
        self.captions["tab"].append((f"{ch}.{n}", caption))
        t = self.doc.add_table(rows=1 + len(rows), cols=len(header)); t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        tblPr = t._tbl.tblPr
        borders = OxmlElement("w:tblBorders")
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            e = OxmlElement(f"w:{edge}"); e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4"); e.set(qn("w:space"), "0"); e.set(qn("w:color"), "808080"); borders.append(e)
        tblPr.append(borders)
        mar = OxmlElement("w:tblCellMar")
        for edge, w in (("top", 30), ("left", 70), ("bottom", 30), ("right", 70)):
            e = OxmlElement(f"w:{edge}"); e.set(qn("w:w"), str(w)); e.set(qn("w:type"), "dxa"); mar.append(e)
        tblPr.append(mar)
        tw = OxmlElement("w:tblW"); tw.set(qn("w:w"), str(int(sum(widths) * 1440))); tw.set(qn("w:type"), "dxa")
        old = tblPr.find(qn("w:tblW"))
        if old is not None: tblPr.remove(old)
        tblPr.append(tw)
        lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); tblPr.append(lay)
        def fill(cell, text, w, hdr=False, al=None, bold=False):
            cell.width = Inches(w)
            tcPr = cell._tc.get_or_add_tcPr()
            if hdr: shade(tcPr, "D9D9D9")
            cell.paragraphs[0].text = ""
            lines = str(text).split("\n")
            for k, ln in enumerate(lines):
                p = cell.paragraphs[0] if k == 0 else cell.add_paragraph()
                self._fmt(p, al if al is not None else WD_ALIGN_PARAGRAPH.LEFT, 1.0, 0)
                self.runs(p, ln, size, bold=hdr or bold)
        for j, h in enumerate(header): fill(t.rows[0].cells[j], h, widths[j], True, WD_ALIGN_PARAGRAPH.CENTER)
        trPr = t.rows[0]._tr.get_or_add_trPr(); th = OxmlElement("w:tblHeader"); trPr.append(th)
        for i, row in enumerate(rows):
            for j, v in enumerate(row):
                al = (align[j] if align else None)
                fill(t.rows[i + 1].cells[j], v, widths[j], False, al, bold=(bold_first_col and j == 0))
        for row in t.rows:
            trPr = row._tr.get_or_add_trPr(); cs = OxmlElement("w:cantSplit"); trPr.append(cs)
        set_col_widths(t, widths)
        if len(rows) <= 9:   # keep small tables on one page
            for row in t.rows[:-1]:
                for cell in row.cells:
                    for pp in cell.paragraphs: pp.paragraph_format.keep_with_next = True
        if note:
            q = self.doc.add_paragraph(); self._fmt(q, WD_ALIGN_PARAGRAPH.LEFT, 1.0, 8, before=3)
            self.runs(q, note, 10, italic=True)
        else:
            q = self.doc.add_paragraph(); self._fmt(q, spacing=1.0, after=6)
        return t

    # ------------------------------------------------------------------ sections / footer
    def footer_page_number(self, section, fmt, start):
        sectPr = section._sectPr
        for tag in ("w:titlePg", "w:pgNumType"):
            for e in sectPr.findall(qn(tag)): sectPr.remove(e)
        pg = OxmlElement("w:pgNumType"); pg.set(qn("w:fmt"), fmt); pg.set(qn("w:start"), str(start)); sectPr.append(pg)
        section.footer.is_linked_to_previous = False
        f = section.footer
        for p in list(f.paragraphs)[1:]: p._p.getparent().remove(p._p)
        p = f.paragraphs[0]
        for r in list(p.runs): r._r.getparent().remove(r._r)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(); set_font(r, 11)
        for t, txt in (("begin", None), (None, " PAGE "), ("end", None)):
            if t:
                fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), t); r._r.append(fc)
            else:
                it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = txt; r._r.append(it)

    def set_margins(self, section):
        section.left_margin = Inches(1.5); section.right_margin = Inches(1.0)
        section.top_margin = Inches(1.0); section.bottom_margin = Inches(1.0)
        section.footer_distance = Inches(0.5)


# ---------------------------------------------------------------------- schema ordering (Word is strict about child order)
_ORDER = {
 "pPr": "pStyle keepNext keepLines pageBreakBefore framePr widowControl numPr suppressLineNumbers pBdr shd tabs suppressAutoHyphens kinsoku wordWrap overflowPunct topLinePunct autoSpaceDE autoSpaceDN bidi adjustRightInd snapToGrid spacing ind contextualSpacing mirrorIndents suppressOverlap jc textDirection textAlignment textboxTightWrap outlineLvl divId cnfStyle rPr sectPr pPrChange",
 "tblPr": "tblStyle tblpPr tblOverlap bidiVisual tblStyleRowBandSize tblStyleColBandSize tblW jc tblCellSpacing tblInd tblBorders shd tblLayout tblCellMar tblLook tblCaption tblDescription",
 "sectPr": "headerReference footerReference footnotePr endnotePr type pgSz pgMar paperSrc pgBorders lnNumType pgNumType cols formProt vAlign noEndnote titlePg textDirection bidi rtlGutter docGrid printerSettings sectPrChange",
 "tcPr": "cnfStyle tcW gridSpan hMerge vMerge tcBorders shd noWrap tcMar textDirection tcFitText vAlign hideMark",
}
_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def fix_order(root):
    for tag, order in _ORDER.items():
        idx = {n: i for i, n in enumerate(order.split())}
        for el in root.iter(_W + tag):
            kids = list(el)
            kids_sorted = sorted(kids, key=lambda k: idx.get(k.tag.replace(_W, ""), 999))
            if kids != kids_sorted:
                for k in kids: el.remove(k)
                for k in kids_sorted: el.append(k)
            if tag == "tblPr":   # drop duplicate tblW / tblLayout if any
                for name in ("tblW", "tblLayout", "tblBorders", "tblCellMar"):
                    found = el.findall(_W + name)
                    for extra in found[:-1]: el.remove(extra)
