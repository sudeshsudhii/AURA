"""Cover page, bonafide, declaration, acknowledgements, abstract, contents and lists."""
import copy
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from report_lib import set_font, shade, set_col_widths

TITLE = "UNDERSTANDING PACKET CAPTURE TIMES IN NETWORK FORENSICS: TIMESTAMPS, TIME SYNCHRONISATION AND ATTACK TIMELINE RECONSTRUCTION"
TITLE_CASE = "Understanding Packet Capture Times in Network Forensics: Timestamps, Time Synchronisation and Attack Timeline Reconstruction"
STUDENTS = [("SUDESH P", "RA2512005010025"), ("HARSH GUPTA", "RA2512005010054"), ("AISHWARYA B", "RA2512005010001")]
COURSE_CODE = "21CSE535T"
COURSE = "Network Intrusions and Computer Forensics"
DEPT = "Department of Computing Technologies"
GUIDE_PLACEHOLDER = "[[Name of the Faculty]]"


def set_text(p, text, keep_highlight=False, size=None):
    """Replace the text of a template paragraph, keeping the first run's formatting."""
    runs = p.runs
    for r in runs[1:]: r._r.getparent().remove(r._r)
    r = runs[0]; r.text = text
    if size: r.font.size = Pt(size)
    if not keep_highlight:
        rpr = r._r.rPr
        if rpr is not None:
            for h in rpr.findall(qn("w:highlight")): rpr.remove(h)


def _sp(p, before=0, after=0, line=1.15):
    """Set exact paragraph spacing (pt) and line spacing (multiple); clears template indents."""
    pf = p.paragraph_format
    pf.space_before = Pt(before); pf.space_after = Pt(after); pf.line_spacing = line
    pf.left_indent = Inches(0); pf.right_indent = Inches(0); pf.first_line_indent = Inches(0)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER


def layout_cover(R, off):
    """Even, compact cover layout (the template's per-line spacing left uneven gaps between the names)."""
    ps = R.doc.paragraphs
    title, course, subm = ps[0], ps[1], ps[2]
    names = ps[3:3 + len(STUDENTS)]
    under, guide, desig, dept = ps[6 + off - 2], ps[7 + off - 2], ps[8 + off - 2], ps[9 + off - 2]
    # after the two blank paragraphs were removed, indices shift by 2
    assert under.text.startswith("Under the guidance"), under.text
    partial, degree, in_p, branch, logo = ps[10 + off - 2], ps[11 + off - 2], ps[12 + off - 2], ps[13 + off - 2], ps[14 + off - 2]
    _sp(title, 0, 8, 1.1)
    _sp(course, 0, 14, 1.15)
    _sp(subm, 0, 6, 1.15)
    for p in names: _sp(p, 0, 3, 1.15)
    _sp(under, 16, 2, 1.15)
    for p in (guide, desig, dept): _sp(p, 0, 2, 1.15)
    # "in partial fulfillment ..." split into three centred lines like the reference report
    set_text(partial, "in partial fulfillment of the requirements for the course"); _sp(partial, 14, 2, 1.15)
    code = copy.deepcopy(partial._p); partial._p.addnext(code)
    from docx.text.paragraph import Paragraph
    code = Paragraph(code, partial._parent)
    set_text(code, f"{COURSE_CODE} – {COURSE.upper()}"); _sp(code, 0, 2, 1.15)
    for r in code.runs: r.font.italic = False; r.font.bold = True
    first_of = next(r for r in degree.runs if r.text == "of")      # only the first "of" (before the line break)
    first_of.text = "for the degree of"
    _sp(degree, 0, 2, 1.15); _sp(in_p, 0, 2, 1.15); _sp(branch, 0, 0, 1.15)
    _sp(logo, 20, 20, 1.0)
    # the institutional block at the bottom keeps the template's 1.5 spacing
    # symmetric cover margins (template had 0.69" left, 0.59" right)
    s0 = R.doc.sections[0]; s0.right_margin = s0.left_margin


def fix_bonafide_header(R):
    """Template put the logo and the institute name in one indented paragraph; split and centre them."""
    from docx.text.paragraph import Paragraph
    ps = R.doc.paragraphs
    hdr = next(p for p in ps if p.text.strip().startswith("SRM INSTITUTION OF SCIENCE"))
    blank_before = Paragraph(hdr._p.getprevious(), hdr._parent)
    _sp(blank_before, 0, 0, 1.0)
    logo_p = copy.deepcopy(hdr._p); hdr._p.addprevious(logo_p); logo_p = Paragraph(logo_p, hdr._parent)
    W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    for r in list(logo_p.runs):
        if r._r.find(".//" + W + "drawing") is None: r._r.getparent().remove(r._r)
    for r in list(hdr.runs):
        if r._r.find(".//" + W + "drawing") is not None: r._r.getparent().remove(r._r)
    # the logo is a floating image placed 0.79" left of the column; anchor it to the centre of the margins
    WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
    for anc in logo_p._p.iter(WP + "anchor"):
        ph = anc.find(WP + "positionH"); pv = anc.find(WP + "positionV")
        for ch in list(ph): ph.remove(ch)
        ph.set("relativeFrom", "margin")
        al = OxmlElement("wp:align"); al.text = "center"; ph.append(al)
        for ch in list(pv): ch.text = "0"
    txt = " ".join(hdr.text.split()).replace("INSTITUTION", "INSTITUTE")
    set_text(hdr, txt)
    _sp(logo_p, 0, 10, 1.0); _sp(hdr, 0, 0, 1.3)
    nxt = Paragraph(hdr._p.getnext(), hdr._parent)          # KATTANKULATHUR line
    set_text(nxt, "KATTANKULATHUR - 603203"); _sp(nxt, 0, 0, 1.3)
    for p in R.doc.paragraphs:
        if p.text == "\t": set_text(p, "")
        if p.text.startswith("BONAFIDE CERTIFICATE"): _sp(p, 18, 12, 1.15)


def edit_cover_and_bonafide(R):
    ps = R.doc.paragraphs
    set_text(ps[0], TITLE, size=16); ps[0].paragraph_format.space_after = Pt(4)
    R.doc.inline_shapes[0].width = Inches(2.1); R.doc.inline_shapes[0].height = Inches(2.1 * 1.669 / 2.916)
    set_text(ps[1], f"{COURSE_CODE} – {COURSE} Course Case Study Project")
    set_text(ps[3], f"{STUDENTS[0][0]} [{STUDENTS[0][1]}]", size=14)
    anchor = ps[3]._p
    for nm, rn in STUDENTS[1:][::-1]:
        e = copy.deepcopy(ps[3]._p); anchor.addnext(e)
    # fix the text of the two copies
    ps = R.doc.paragraphs
    for k, (nm, rn) in enumerate(STUDENTS):
        set_text(ps[3 + k], f"{nm} [{rn}]", size=14)
        ps[3 + k].paragraph_format.right_indent = Inches(0); ps[3 + k].paragraph_format.left_indent = Inches(0)   # template indent pulled the names left of centre
    ps[0].paragraph_format.left_indent = Inches(0); ps[0].paragraph_format.right_indent = Inches(0)
    off = len(STUDENTS) - 1
    set_text(ps[7 + off], "Dr. RAJASEKARAN P")
    set_text(ps[8 + off], "Assistant Professor")
    set_text(ps[9 + off], DEPT)
    set_text(ps[10 + off], f"in partial fulfillment of the requirements for the course {COURSE_CODE} – {COURSE.upper()} for the degree ")
    p11 = ps[11 + off]
    for r in p11.runs:
        if "Batchelor" in r.text: r.text = "Master "
        elif r.text == "Of": r.text = "of"
    set_text(ps[13 + off], "COMPUTER SCIENCE ENGINEERING")
    for q in (ps[4 + off], ps[5 + off]):
        if not q.text.strip(): q._p.getparent().remove(q._p)
    layout_cover(R, off)
    fix_bonafide_header(R)
    # bonafide paragraph
    bp = None
    for p in R.doc.paragraphs:
        if p.text.startswith("This is to certify"): bp = p; break
    for r in list(bp.runs): r._r.getparent().remove(r._r)
    def add(t, bold=False, hl=False):
        r = bp.add_run(t); set_font(r, 14, bold)
        if hl: r.font.highlight_color = WD_COLOR_INDEX.YELLOW
    add(f"This is to certify that {COURSE_CODE} – {COURSE} case study report titled “")
    add(TITLE_CASE, bold=True)
    add("” is the bonafide work of")
    # names on their own centred lines (inline bold names with long register numbers stretched the justified lines)
    from docx.text.paragraph import Paragraph
    anchor = bp._p
    for nm, rn in STUDENTS:
        e = copy.deepcopy(bp._p); anchor.addnext(e); anchor = e
        q = Paragraph(e, bp._parent)
        for r in list(q.runs): r._r.getparent().remove(r._r)
        r = q.add_run(f"{nm} [{rn}]"); set_font(r, 13, True)
        _sp(q, 0, 2, 1.3)
    q0 = Paragraph(anchor, bp._parent); q0.paragraph_format.space_after = Pt(8)
    e = copy.deepcopy(bp._p); anchor.addnext(e); q = Paragraph(e, bp._parent)
    for r in list(q.runs): r._r.getparent().remove(r._r)
    r = q.add_run("who undertook the task of completing the report within the allotted time."); set_font(r, 14)
    first = Paragraph(bp._p.getnext(), bp._parent); first.paragraph_format.space_before = Pt(8)
    # signature table
    t = R.doc.tables[0]
    for p in t.rows[0].cells[0].paragraphs:
        if "Name of the Faculty" in p.text: set_text(p, "Dr. RAJASEKARAN P")
        elif "Computational Intelligence" in p.text: set_text(p, DEPT)
    tp = tbl_pr = t._tbl.tblPr
    for e in tbl_pr.findall(qn("w:tblpPr")): tbl_pr.remove(e)
    set_col_widths(t, [3.4, 2.37])
    # remove the template's blank spacer paragraphs and the guidance text that follows the bonafide table
    body = R.body
    tbl = t._tbl
    el = tbl.getnext()
    while el is not None and el.tag != qn("w:sectPr"):
        nxt = el.getnext(); body.remove(el); el = nxt


def front_matter(R, pages, captions, abbrevs):
    d = R.doc
    # ------------------------------------------------------------ declaration
    R.plain_title(f"{DEPT}", size=13, after=0)
    R.center("SRM Institute of Science & Technology", 13, True, after=10)
    R.center("Own Work Declaration Form", 14, True, after=10)
    R.P("This sheet must be filled in, signed, dated with student registration number and included with all assignments submitted for evaluation.", size=11, after=4).paragraph_format.line_spacing = 1.15
    t = d.add_table(rows=4, cols=2); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    data = [("Degree / Course", f"M.Tech / {COURSE_CODE} – {COURSE}"), ("Case Study Topic", "Packet Capture Times in Network Forensics"),
            ("Student Names and Registration Numbers", "\n".join(f"{i+1}. {n} ({r})" for i, (n, r) in enumerate(STUDENTS))), ("Title of Work", TITLE_CASE)]
    _grid(t, [1.9, 3.87]); set_col_widths(t, [1.9, 3.87])
    for i, (a, b) in enumerate(data):
        _cell(t.rows[i].cells[0], a, 11, True, 1.9); _cell(t.rows[i].cells[1], b, 11, False, 3.87)
    R.P("", after=0).paragraph_format.line_spacing = 0.6
    R.P("We hereby certify that this assessment complies with the University rules and regulations relating to academic misconduct and plagiarism. We confirm that all work contained in this report is our own except where indicated through citation and acknowledgement, and that we have:", size=11, after=3).paragraph_format.line_spacing = 1.15
    for s in ("Clearly referenced and listed all sources as appropriate.",
              "Referenced and put in inverted commas all quoted text from books, documentation or other sources.",
              "Given the sources of all pictures, diagrams, data and code that are not our own.",
              "Not made use of the report or essay of any other student, either past or present.",
              "Acknowledged any help received from others.",
              "Complied with any other plagiarism criteria specified by the course handbook or University website."):
        p = d.add_paragraph(style="List Bullet"); R._fmt(p, WD_ALIGN_PARAGRAPH.JUSTIFY, 1.1, 1, indent=0.5, first=-0.25); R.runs(p, s, 11)
    R.P("**DECLARATION:** We are aware of and understand the University policy on academic misconduct and plagiarism. We certify that this assessment is our own work, except where indicated by referencing, and that we have followed good academic practices.", size=11, after=8, before=6).paragraph_format.line_spacing = 1.15
    t = d.add_table(rows=1 + len(STUDENTS), cols=4); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    w = [1.2, 2.1, 1.5, 0.97]; _grid(t, w); set_col_widths(t, w)
    for j, h in enumerate(["Student Signature", "Student Name", "Registration Number", "Date"]): _cell(t.rows[0].cells[j], h, 10.5, True, w[j], fill="D9D9D9")
    for i, (n, r) in enumerate(STUDENTS):
        for j, v in enumerate(["", n, r, ""]): _cell(t.rows[i + 1].cells[j], v, 10.5, False, w[j], height=0.42)

    # ------------------------------------------------------------ acknowledgements
    R.plain_title("ACKNOWLEDGEMENTS")
    for txt in (
        "We express our sincere gratitude to Dr. C. Muthamizhchelvan, Vice-Chancellor, SRM Institute of Science and Technology, for the facilities and the academic environment that made this study possible.",
        "We thank Dr. Leenus Jesu Martin M, Dean, College of Engineering and Technology, for his support throughout our programme.",
        "We are grateful to Dr. Revathi Venkataraman, Professor and Chairperson, School of Computing, and to Dr. M. Pushpalatha and Dr. C. Lakshmi, Associate Chairpersons of the School of Computing, for their encouragement and guidance.",
        "We thank Dr. G. Niranjana, Professor and Head, Department of Computing Technologies, for the departmental facilities and her continued support.",
        "We are deeply indebted to our course faculty and guide, Dr. Rajasekaran P, Assistant Professor, Department of Computing Technologies, who teaches 21CSE535T Network Intrusions and Computer Forensics, for the lectures, the feedback on our seminar presentation on packet capture times and the direction he gave this report.",
        "We also thank Dr. J. Selvin Paul Peter, Professor, our faculty advisor, the course coordinators and the department staff for their help, and our families and friends for their patience and support."):
        R.P(txt, first=0.5)
    for nm, rn in STUDENTS:
        R.P(nm, align=WD_ALIGN_PARAGRAPH.RIGHT, after=0)

    # ------------------------------------------------------------ abstract
    R.plain_title("ABSTRACT")
    ab = ("Every packet in a network capture appears to carry a time, yet that time is not part of the packet: the capture program reads its own clock when it sees the frame and stores the value beside it. The success of a network investigation therefore depends on how that clock was kept, how the value is stored and displayed, and how it is compared with other systems. This case study examines packet capture times in network forensics, following Messier’s Network Forensics, with the 2013 Target data breach as the real-world case. The main ideas were reproduced in a working environment. A five-frame capture with the sample timestamp 17:40:01.212754 was decoded by an independent parser, tcpdump 4.99.4 and tshark 4.2.2, which agreed on every value; the raw bytes confirmed that the time is stored as 1794246001 seconds plus 212,754 microseconds. A live loopback capture showed machine-speed gaps of 4 to 215 microseconds and two scripted pauses recorded as 0.800260 s and 1.500237 s. A drift model showed that a 20 ppm clock reaches a ten-minute error after 347 days, and a five-step procedure (record, convert, correct, merge, validate) restored the order of events from five sources scrambled by time zones and clock offsets. A labelled synthetic test showed that an exfiltration window of 10:00 to 18:00 US Central time appears as 16:00 to 24:00 in UTC. Investigators should synchronise clocks with NTP, record times in UTC, state precision and display format, and verify clock offsets before correlating evidence.")
    p = d.add_paragraph(); R._fmt(p, WD_ALIGN_PARAGRAPH.JUSTIFY, 1.5, 8)
    r = p.add_run(ab); set_font(r, 14)
    p = d.add_paragraph(); R._fmt(p, WD_ALIGN_PARAGRAPH.LEFT, 1.15, 0)
    R.runs(p, "**Keywords:** Packet Capture, Timestamps, pcap, tcpdump, Wireshark, Epoch Time, UTC, NTP, Clock Drift, Timeline Reconstruction, Network Forensics, Target Data Breach", 12)
    return ab


def _grid(t, widths):
    tblPr = t._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{edge}"); e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4"); e.set(qn("w:space"), "0"); e.set(qn("w:color"), "000000"); borders.append(e)
    tblPr.append(borders)
    lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); tblPr.append(lay)


def _cell(cell, text, size, bold, w, fill=None, height=None):
    from report_lib import set_font
    cell.width = Inches(w)
    if fill: shade(cell._tc.get_or_add_tcPr(), fill)
    lines = str(text).split("\n")
    for k, ln in enumerate(lines):
        p = cell.paragraphs[0] if k == 0 else cell.add_paragraph()
        p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.1
        r = p.add_run(ln); set_font(r, size, bold)
    if height:
        trPr = cell._tc.getparent().get_or_add_trPr(); h = OxmlElement("w:trHeight"); h.set(qn("w:val"), str(int(height * 1440))); h.set(qn("w:hRule"), "atLeast"); trPr.append(h)


def contents(R, toc_entries, pages, captions, abbrevs):
    d = R.doc
    def pg(key): return str(pages.get(key, ""))
    # ---------------------------------------------------------------- TOC
    R.plain_title("TABLE OF CONTENTS", size=14, after=8)
    t = d.add_table(rows=1, cols=3); w = [1.1, 3.85, 0.82]
    _noborder(t)
    for j, h in enumerate(["Chapter No", "Title", "Page No"]):
        _cell(t.rows[0].cells[j], h, 11.5, True, w[j]); t.rows[0].cells[j].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER if j != 1 else WD_ALIGN_PARAGRAPH.LEFT
    for num, title, level, key in toc_entries:
        row = t.add_row()
        vals = [num, title, pg(key)]
        for j, v in enumerate(vals):
            _cell(row.cells[j], v, 11.5, level == 0, w[j])
            row.cells[j].paragraphs[0].paragraph_format.space_after = Pt(2.5)
            if j != 1: row.cells[j].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif level == 1: row.cells[j].paragraphs[0].paragraph_format.left_indent = Inches(0.0)
    set_col_widths(t, w)
    # ---------------------------------------------------------------- LoF / LoT
    for title, key, items in (("LIST OF FIGURES", "fig", captions.get("fig", [])), ("LIST OF TABLES", "tab", captions.get("tab", []))):
        R.plain_title(title, size=14, after=8)
        t = d.add_table(rows=1, cols=3); w = [0.6, 4.45, 0.72]; _noborder(t)
        for j, h in enumerate(["No.", "Title", "Page No"]):
            _cell(t.rows[0].cells[j], h, 11.5, True, w[j]); t.rows[0].cells[j].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER if j != 1 else WD_ALIGN_PARAGRAPH.LEFT
        for no, cap in items:
            row = t.add_row()
            for j, v in enumerate([no, cap, str(pages.get(f"{key}:{no}", ""))]):
                _cell(row.cells[j], v, 11, False, w[j]); row.cells[j].paragraphs[0].paragraph_format.space_after = Pt(4)
                if j != 1: row.cells[j].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_col_widths(t, w)
    # ---------------------------------------------------------------- abbreviations
    R.plain_title("LIST OF ABBREVIATIONS", size=14, after=8)
    t = d.add_table(rows=0, cols=2); w = [1.2, 4.57]; _noborder(t)
    for a, b in abbrevs:
        row = t.add_row()
        for j, v in enumerate([a, b]):
            _cell(row.cells[j], v, 11.5, j == 0, w[j]); row.cells[j].paragraphs[0].paragraph_format.space_after = Pt(3)
    set_col_widths(t, w)


def _noborder(t):
    tblPr = t._tbl.tblPr
    lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); tblPr.append(lay)
