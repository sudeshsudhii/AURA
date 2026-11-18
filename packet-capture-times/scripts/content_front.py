"""Front matter built to match the reference report (21CSE535T case study, Nov. 2026) line for line:
cover, bonafide certificate, own-work declaration, acknowledgements, abstract, contents and lists.
Sizes/spacing were measured from the reference PDF (pdftohtml): see layout notes beside each block."""
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH as AL, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from report_lib import set_font, shade, set_col_widths

TITLE = "UNDERSTANDING PACKET CAPTURE TIMES IN NETWORK FORENSICS: TIMESTAMPS, TIME SYNCHRONISATION AND ATTACK TIMELINE RECONSTRUCTION"
TITLE_CASE = "Understanding Packet Capture Times in Network Forensics: Timestamps, Time Synchronisation and Attack Timeline Reconstruction"
TOPIC = "Packet Capture Times"
STUDENTS = [("SUDESH P", "RA2512005010025"), ("HARSH GUPTA", "RA2512005010054"), ("AISHWARYA B", "RA2512005010001")]
COURSE_CODE = "21CSE535T"
COURSE = "Network Intrusions and Computer Forensics"
GUIDE = "Dr. RAJASEKARAN P"
DEPT = "Department of Computing Technologies"


# ---------------------------------------------------------------------------- primitives
def line(R, text, size=12, bold=False, italic=False, before=0, after=0, spacing=1.0, align=AL.CENTER, page_break=False):
    p = R.doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(before); pf.space_after = Pt(after); pf.line_spacing = spacing
    pf.left_indent = Inches(0); pf.first_line_indent = Inches(0)
    p.alignment = align
    if page_break: pf.page_break_before = True
    if text:
        R.runs(p, text, size, bold, italic)
    return p


def title16(R, text, page_break=True, after=22):
    """Front-matter page title: 16 pt bold, centred (reference: ACKNOWLEDGEMENTS, ABSTRACT, TABLE OF CONTENTS ...)."""
    p = line(R, f"**{text}**", 16, before=0, after=after, spacing=1.0, page_break=page_break)
    p.paragraph_format.keep_with_next = True
    return p


def _borders(t, color="000000", sz=4, inside=True):
    tblPr = t._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right") + (("insideH", "insideV") if inside else ()):
        e = OxmlElement(f"w:{edge}"); e.set(qn("w:val"), "single"); e.set(qn("w:sz"), str(sz)); e.set(qn("w:space"), "0"); e.set(qn("w:color"), color); b.append(e)
    tblPr.append(b)


def _cell(R, cell, text, size, bold=False, align=AL.LEFT, spacing=1.0, after=0, fill=None, height=None):
    if fill: shade(cell._tc.get_or_add_tcPr(), fill)
    for k, ln in enumerate(str(text).split("\n")):
        p = cell.paragraphs[0] if k == 0 else cell.add_paragraph()
        p.paragraph_format.space_after = Pt(after); p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.line_spacing = spacing; p.alignment = align
        if ln: R.runs(p, ln, size, bold)
    if height:
        trPr = cell._tc.getparent().get_or_add_trPr(); h = OxmlElement("w:trHeight")
        h.set(qn("w:val"), str(int(height * 1440))); h.set(qn("w:hRule"), "atLeast"); trPr.append(h)


# ---------------------------------------------------------------------------- cover (section with 1" margins)
def cover(R, logo_path):
    # reference tops: title 101/125/148, A CASE STUDY REPORT 185, topic 205, Submitted by 229, names 255/278/301,
    # Under the Guidance of 331, guide 353, designation 380, in partial 401, course 425, MASTER 451, in 476,
    # COMPUTER SCIENCE ENGINEERING 501, logo 534-608 (130 x 74 pt), DEPARTMENT 627 ... KATTANKULATHUR 699, NOVEMBER 2026 721
    line(R, f"**{TITLE}**", 18, before=20, after=10, spacing=1.13)
    line(R, "**A CASE STUDY REPORT**", 14, after=4)
    line(R, f"(Case Study Topic: {TOPIC})", 12, after=10)
    line(R, "*Submitted by*", 14, after=10)
    for k, (n, r) in enumerate(STUDENTS):
        line(R, f"**{n} [{r}]**", 15, after=13 if k == len(STUDENTS) - 1 else 5.75)
    line(R, "*Under the Guidance of*", 14, after=6)
    line(R, f"**{GUIDE}**", 16, after=9)
    line(R, f"(Assistant Professor, {DEPT})", 12, after=7)
    line(R, "*in partial fulfilment of the requirements for the course*", 14, after=8)
    line(R, f"**{COURSE_CODE} - {COURSE.upper()}**", 14, after=10)
    line(R, "**MASTER OF TECHNOLOGY**", 16, after=6.6)
    line(R, "in", 16, after=6.6)
    line(R, "**COMPUTER SCIENCE ENGINEERING**", 16, after=0)
    p = line(R, "", 12, before=8, after=11)   # 7 pt less each side: our title runs to four lines
    p.add_run().add_picture(logo_path, width=Inches(1.806))
    for t in ("DEPARTMENT OF COMPUTING TECHNOLOGIES", "COLLEGE OF ENGINEERING AND TECHNOLOGY",
              "SRM INSTITUTE OF SCIENCE AND TECHNOLOGY", "KATTANKULATHUR - 603 203"):
        line(R, f"**{t}**", 14, spacing=1.5)
    line(R, "**NOVEMBER 2026**", 12, spacing=1.0)


# ---------------------------------------------------------------------------- front matter (section with 1.5"/1" margins)
def bonafide(R):
    # reference: header 14 pt bold at 72/96, title 16 pt at 140, body 12 pt 1.5 lines, names 12 pt bold centred,
    # SIGNATURE at 482, name/designation/department 12 pt single-spaced from 527
    line(R, "**SRM INSTITUTE OF SCIENCE AND TECHNOLOGY**", 14, spacing=1.5)
    line(R, "**KATTANKULATHUR - 603 203**", 14, spacing=1.5, after=20)
    line(R, "**BONAFIDE CERTIFICATE**", 16, after=28)
    line(R, f"Certified that {COURSE_CODE} - {COURSE} case study report titled \"{TITLE_CASE}\" is the bonafide work of",
         12, spacing=1.5, align=AL.JUSTIFY, after=6)
    for n, r in STUDENTS:
        line(R, f"**{n} [{r}]**", 12, spacing=1.5)
    line(R, "who carried out the case study under my supervision. Certified further, that to the best of my knowledge the work "
            "reported herein does not form any other project report or dissertation on the basis of which a degree or award was "
            "conferred on an earlier occasion on this or any other candidate.", 12, spacing=1.5, align=AL.JUSTIFY, before=6)
    line(R, "SIGNATURE", 12, align=AL.LEFT, before=76, after=30)
    for t in (GUIDE, "ASSISTANT PROFESSOR", DEPT.upper()):
        line(R, t, 12, align=AL.LEFT, spacing=1.15)


def declaration(R):
    d = R.doc
    line(R, f"**{DEPT}**", 12, spacing=1.15, page_break=True)
    line(R, "**SRM Institute of Science & Technology**", 12, spacing=1.15, after=10)
    line(R, "**Own Work Declaration Form**", 14, after=12)
    line(R, "This sheet must be filled in, signed, dated with student registration number, and included with all assignments submitted for evaluation.",
         12, spacing=1.15, align=AL.JUSTIFY, after=10)
    t = d.add_table(rows=5, cols=2); t.alignment = WD_TABLE_ALIGNMENT.CENTER; _borders(t)
    rows = [("**Field**", "**Details**"), ("Degree / Course", f"M.Tech / {COURSE_CODE} - {COURSE}"), ("Case Study Topic", TOPIC),
            ("Student Names and Registration Numbers", "\n".join(f"{i+1}. {n} ({r})" for i, (n, r) in enumerate(STUDENTS))),
            ("Title of Work", TITLE_CASE)]
    for i, (a, b) in enumerate(rows):
        _cell(R, t.rows[i].cells[0], a, 11, spacing=1.05, after=1); _cell(R, t.rows[i].cells[1], b, 11, spacing=1.05, after=1)
    set_col_widths(t, [1.5, 4.27])
    line(R, "We hereby certify that this assessment complies with the University rules and regulations relating to academic misconduct "
            "and plagiarism. We confirm that all work contained in this report is our own except where indicated through citation and "
            "acknowledgement, and that we have:", 12, spacing=1.15, align=AL.JUSTIFY, before=10, after=4)
    for s in ("Clearly referenced and listed all sources as appropriate.",
              "Referenced and put in inverted commas all quoted text from books, documentation, or other sources.",
              "Given the sources of all pictures, diagrams, data, and code that are not our own.",
              "Not made use of the report or essay of any other student either past or present.",
              "Acknowledged any help received from others.",
              "Complied with any other plagiarism criteria specified by the course handbook or University website."):
        p = d.add_paragraph(style="List Bullet")
        R._fmt(p, AL.LEFT, 1.15, 6, indent=0.25, first=-0.25); R.runs(p, s, 12)   # reference: 20 pt between items
    line(R, "**DECLARATION:** We are aware of and understand the University policy on academic misconduct and plagiarism. We certify "
            "that this assessment is our own work, except where indicated by referencing, and that we have followed good academic practices.",
         12, spacing=1.15, align=AL.JUSTIFY, before=6, after=10)
    t = d.add_table(rows=1 + len(STUDENTS), cols=4); t.alignment = WD_TABLE_ALIGNMENT.CENTER; _borders(t)
    for j, h in enumerate(["Student Signature", "Student Name", "Registration Number", "Date"]):
        _cell(R, t.rows[0].cells[j], f"**{h}**", 10)
    for i, (n, r) in enumerate(STUDENTS):
        for j, v in enumerate(["", n, r, ""]): _cell(R, t.rows[i + 1].cells[j], v, 10, height=0.3)
    set_col_widths(t, [1.26, 2.53, 1.5, 0.48])


def acknowledgements(R):
    title16(R, "ACKNOWLEDGEMENTS", after=24)
    paras = (
        "We thank Dr. C. Muthamizhchelvan, Vice-Chancellor, SRM Institute of Science and Technology, for the facilities the Institute provided for this study.",
        "We are grateful to Dr. Leenus Jesu Martin M, Dean-CET, SRM Institute of Science and Technology, for his support.",
        "Our thanks also go to Dr. Revathi Venkataraman, Professor and Chairperson, School of Computing, and to Dr. M. Pushpalatha, Professor and Associate Chairperson - CS, and Dr. C. Lakshmi, Professor and Associate Chairperson - AI, School of Computing, for their support during the course.",
        "We thank Dr. G. Niranjana, Professor and Head, Department of Computing Technologies, for her encouragement and for the department's facilities.",
        "We owe the most to our course faculty and guide for this case study, Dr. Rajasekaran P, Assistant Professor, Department of Computing Technologies, who teaches 21CSE535T Network Intrusions and Computer Forensics, for his guidance and feedback from our seminar presentation on packet capture times through to this report.",
        "We extend our sincere thanks to Dr. J. Selvin Paul Peter, Professor, our faculty advisor, for his academic guidance and support in completing this work.",
        "We also thank the course coordinators and the department staff for their help, and our parents, families and friends for their patience and support.")
    for t in paras:
        p = line(R, t, 12, spacing=1.5, align=AL.JUSTIFY, after=9)
        p.paragraph_format.first_line_indent = Inches(0.4)
    for k, (n, _) in enumerate(STUDENTS):
        p = line(R, n, 12, spacing=1.5, align=AL.LEFT, before=24 if k == 0 else 0)
        p.paragraph_format.left_indent = Inches(2.93)


ABSTRACT = ("Every packet in a network capture appears to carry a time, yet that time is not part of the packet: the capture program reads its own clock when it sees the frame and stores the value beside it. The success of a network investigation therefore depends on how that clock was kept, how the value is stored and displayed, and how it is compared with other systems. This case study examines packet capture times in network forensics, following Messier’s Network Forensics, with the 2013 Target data breach as the real-world case. The main ideas were reproduced in a working environment. A five-frame capture with the sample timestamp 17:40:01.212754 was decoded by an independent parser, tcpdump 4.99.4 and tshark 4.2.2, which agreed on every value; the raw bytes confirmed that the time is stored as 1794246001 seconds plus 212,754 microseconds. A live loopback capture showed machine-speed gaps of 4 to 215 microseconds and two scripted pauses recorded as 0.800260 s and 1.500237 s. A drift model showed that a 20 ppm clock reaches a ten-minute error after 347 days, and a five-step procedure (record, convert, correct, merge, validate) restored the order of events from five sources scrambled by time zones and clock offsets. A labelled synthetic test showed that an exfiltration window of 10:00 to 18:00 US Central time appears as 16:00 to 24:00 in UTC. Investigators should synchronise clocks with NTP, record times in UTC, state precision and display format, and verify clock offsets before correlating evidence.")
KEYWORDS = "Packet Capture, Timestamps, pcap, tcpdump, Wireshark, Epoch Time, UTC, NTP, Clock Drift, Timeline Reconstruction, Network Forensics, Target Data Breach"


def abstract(R):
    # reference: title 16 pt bold; body 14 pt, 1.5 lines, justified; "Keywords:" bold 12 pt, 1.5 lines
    title16(R, "ABSTRACT", after=27)
    line(R, ABSTRACT, 14, spacing=1.5, align=AL.JUSTIFY, after=14)
    line(R, f"**Keywords:** {KEYWORDS}", 12, spacing=1.5, align=AL.LEFT)


# ---------------------------------------------------------------------------- contents and lists
def contents(R, toc_entries, pages, captions, abbrevs):
    d = R.doc
    pg = lambda k: str(pages.get(k, ""))
    # TABLE OF CONTENTS - reference: no borders, header bold 12 pt, rows ~32 pt apart, chapter rows bold
    title16(R, "TABLE OF CONTENTS", after=33)
    w = [1.06, 3.49, 1.22]
    t = d.add_table(rows=1, cols=3); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(["Chapter No", "Title", "Page No"]):
        _cell(R, t.rows[0].cells[j], f"**{h}**", 12, align=AL.CENTER, spacing=1.0, after=18)
    for num, ttl, level, key in toc_entries:
        cells = t.add_row().cells
        b = "**" if level == 0 and (num or ttl in ("REFERENCES", "APPENDICES")) else ""
        _cell(R, cells[0], f"{b}{num}{b}" if num else "", 12, align=AL.CENTER, spacing=1.15, after=15.5)
        _cell(R, cells[1], f"{b}{ttl}{b}", 12, align=AL.LEFT, spacing=1.15, after=15.5)
        _cell(R, cells[2], f"{b}{pg(key)}{b}" if pg(key) else "", 12, align=AL.CENTER, spacing=1.15, after=15.5)
    set_col_widths(t, w)
    # LIST OF FIGURES / TABLES - reference: NO. | TITLE | PAGE NO. (bold), 12 pt, no borders
    for ttl, kind in (("LIST OF FIGURES", "fig"), ("LIST OF TABLES", "tab")):
        title16(R, ttl, after=29)
        t = d.add_table(rows=1, cols=3); t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for j, h in enumerate(["NO.", "TITLE", "PAGE\nNO."]):
            c = t.rows[0].cells[j]
            _cell(R, c, "\n".join(f"**{x}**" for x in h.split("\n")), 12, align=AL.LEFT if j == 1 else AL.CENTER, spacing=1.0, after=2)
            c.paragraphs[-1].paragraph_format.space_after = Pt(8)
        for no, cap in captions.get(kind, []):
            cells = t.add_row().cells
            _cell(R, cells[0], no, 12, align=AL.CENTER, spacing=1.0, after=6)
            _cell(R, cells[1], cap, 12, align=AL.LEFT, spacing=1.0, after=6)
            _cell(R, cells[2], pg(f"{kind}:{no}"), 12, align=AL.CENTER, spacing=1.0, after=6)
        set_col_widths(t, [1.03, 4.09, 0.65])
    # LIST OF ABBREVIATIONS - reference: bold abbreviation, 12 pt, rows ~17 pt apart
    title16(R, "LIST OF ABBREVIATIONS", after=27)
    t = d.add_table(rows=0, cols=2); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for a, b in abbrevs:
        cells = t.add_row().cells
        _cell(R, cells[0], f"**{a}**", 12, spacing=1.0, after=3); _cell(R, cells[1], b, 12, spacing=1.0, after=3)
    set_col_widths(t, [1.43, 4.34])
