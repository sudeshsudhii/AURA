#!/usr/bin/env python3
"""Build the case study report from the SRMIST template.  Run from the scripts/ directory:
    python3 build_report.py <template.docx> <out.docx>
Pass 1 collects figure/table captions; pass 2 renders to PDF to find page numbers; pass 3 writes the final file."""
import io, json, os, re, subprocess, sys, shutil, zipfile
from docx.shared import Inches
from docx.oxml.ns import qn
from docx.enum.section import WD_SECTION
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from report_lib import Report, fix_order
import content_front as F, content_ch12 as A, content_ch34 as B, content_ch56 as Cc

ABBREV = [("ACK", "Acknowledgement (TCP flag)"), ("ARP", "Address Resolution Protocol"), ("CO", "Course Outcome"),
          ("DDoS", "Distributed Denial of Service"), ("FCS", "Frame Check Sequence"), ("FTP", "File Transfer Protocol"),
          ("GPS", "Global Positioning System"), ("HVAC", "Heating, Ventilation and Air Conditioning"),
          ("ICMP", "Internet Control Message Protocol"), ("IDS", "Intrusion Detection System"),
          ("IETF", "Internet Engineering Task Force"), ("IP", "Internet Protocol"), ("IST", "Indian Standard Time"),
          ("MAC", "Media Access Control"), ("NIC", "Network Interface Card"), ("NIST", "National Institute of Standards and Technology"),
          ("NTP", "Network Time Protocol"), ("pcap / pcapng", "Packet capture file formats (libpcap and its next-generation successor)"),
          ("POS", "Point of Sale"), ("ppm", "Parts per million"), ("RAM", "Random Access Memory"), ("RFC", "Request for Comments"),
          ("SIEM", "Security Information and Event Management"), ("SPAN", "Switched Port Analyzer (port mirroring)"),
          ("SSH", "Secure Shell"), ("SYN", "Synchronise (TCP flag)"), ("TCP", "Transmission Control Protocol"),
          ("TLS", "Transport Layer Security"), ("TTL", "Time To Live"), ("UDP", "User Datagram Protocol"),
          ("UTC", "Coordinated Universal Time"), ("µs", "Microsecond (10⁻⁶ s)")]

TOC = [("", "Abstract", 0, "ABSTRACT"), ("", "List of Figures", 0, "LIST OF FIGURES"), ("", "List of Tables", 0, "LIST OF TABLES"),
       ("", "List of Abbreviations", 0, "LIST OF ABBREVIATIONS"),
       ("1", "INTRODUCTION", 0, "CHAPTER 1"), ("1.1", "Background", 1, "1.1 Background"),
       ("1.2", "Industry/Domain Context", 1, "1.2 Industry/Domain Context"), ("1.3", "Problem Statement", 1, "1.3 Problem Statement"),
       ("1.4", "Objectives", 1, "1.4 Objectives"), ("1.5", "Scope and Limitations", 1, "1.5 Scope and Limitations"),
       ("1.6", "Organization of the Report", 1, "1.6 Organization of the Report"),
       ("2", "LITERATURE SURVEY", 0, "CHAPTER 2"), ("2.1", "Introduction", 1, "2.1 Introduction"),
       ("2.2", "Review of Existing Approaches", 1, "2.2 Review of Existing Approaches"),
       ("2.3", "Comparative Analysis and Gap Identification", 1, "2.3 Comparative Analysis"),
       ("3", "METHODOLOGY", 0, "CHAPTER 3"), ("3.1", "Approach Overview", 1, "3.1 Approach Overview"),
       ("3.2", "Data Collection / Requirements Gathering", 1, "3.2 Data Collection"), ("3.3", "Architecture", 1, "3.3 Architecture"),
       ("3.4", "Implementation Strategy", 1, "3.4 Implementation Strategy"),
       ("4", "IMPLEMENTATION", 0, "CHAPTER 4"), ("4.1", "Execution and Step-by-Step Analysis", 1, "4.1 Execution"),
       ("4.2", "Core Algorithms and Configurations", 1, "4.2 Core Algorithms"), ("4.3", "Challenges Faced and Mitigation", 1, "4.3 Challenges Faced"),
       ("5", "RESULTS AND DISCUSSION", 0, "CHAPTER 5"), ("5.1", "Findings and Output", 1, "5.1 Findings and Output"),
       ("5.2", "Discussion", 1, "5.2 Discussion"), ("5.3", "Practical Implications", 1, "5.3 Practical Implications"),
       ("6", "CONCLUSION AND FUTURE SCOPE", 0, "CHAPTER 6"), ("6.1", "Conclusion", 1, "6.1 Conclusion"),
       ("6.2", "Future Scope", 1, "6.2 Future Scope"),
       ("", "REFERENCES", 0, "REFERENCES"), ("", "APPENDICES", 0, "APPENDIX A")]
FRONT_KEYS = {"ABSTRACT", "LIST OF FIGURES", "LIST OF TABLES", "LIST OF ABBREVIATIONS"}

TREE = """packet-capture-times/
  scripts/  make_pcap.py parse_pcap.py live_capture.sh gap_analysis.py
            timeline_merge.py drift_model.py tz_table.py exfil_window.py
            figures.py report_lib.py content_*.py build_report.py
  data/     handshake_us.pcap handshake_ns.pcap handshake.pcapng
            live_lo.pcap exfil_hist.json
  output/   parse_us.txt tcpdump_formats.txt tshark_formats.txt
            gap_analysis.txt timeline_merge.txt drift_model.txt
            tz_table.txt exfil_window.txt precision_checks.txt
  figures/  fig_*.png"""


def build(template, out, pages, captions):
    R = Report(template)
    R.captions = {"fig": [], "tab": []}
    d = R.doc
    # start from an empty body: keep the template's styles and its SRM logo, but lay out every page as the reference does
    body = d.element.body
    for el in list(body):
        if el.tag != qn("w:sectPr"): body.remove(el)
    sp = body.find(qn("w:sectPr"))
    for tag in ("w:headerReference", "w:footerReference", "w:titlePg", "w:pgNumType"):
        for e in sp.findall(qn(tag)): sp.remove(e)
    logo = io.BytesIO(zipfile.ZipFile(template).read("word/media/image1.png"))
    F.cover(R, logo)
    d.add_section(WD_SECTION.NEW_PAGE)                      # section 0 = cover
    F.bonafide(R); F.declaration(R); F.acknowledgements(R); F.abstract(R)
    F.contents(R, TOC, pages, captions, ABBREV)
    d.add_section(WD_SECTION.NEW_PAGE)                      # section 1 = front matter, section 2 = chapters
    s0, s1, s2 = d.sections
    s0.left_margin = s0.right_margin = s0.top_margin = s0.bottom_margin = Inches(1.0)
    for s in (s1, s2): R.set_margins(s)
    s0.footer.is_linked_to_previous = False                 # cover: no page number (counts as i)
    R.footer_page_number(s1, "lowerRoman", 2)
    R.footer_page_number(s2, "decimal", 1)
    A.ch1(R); A.ch2(R); B.ch3(R); B.ch4(R); Cc.ch5(R); Cc.ch6(R); Cc.refs_and_appendices(R, TREE)
    d.core_properties.title = F.TITLE_CASE
    d.core_properties.author = ", ".join(n for n, _ in F.STUDENTS)
    fix_order(d.element)
    for s in d.sections: fix_order(s.footer._element)
    d.save(out)
    return R.captions


def to_pdf(docx_path, outdir):
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", outdir, docx_path], capture_output=True, timeout=300)
    return os.path.join(outdir, os.path.basename(docx_path).replace(".docx", ".pdf"))


def roman(n):
    vals = [(10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]; s = ""
    for v, r in vals:
        while n >= v: s += r; n -= v
    return s


def compute_pages(pdf, captions):
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1))
    texts = []
    for i in range(1, n + 1):
        t = subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), "-layout", pdf, "-"], capture_output=True, text=True).stdout
        texts.append([re.sub(r"\s+", " ", ln).strip() for ln in t.split("\n") if ln.strip()])
    p0 = next(i for i, ls in enumerate(texts) if "CHAPTER 1" in ls)
    pages = {}
    def find(prefix, lo, hi):
        for i in range(lo, hi):
            if any(l.startswith(prefix) for l in texts[i]): return i
        return None
    for _, _, _, key in TOC:
        if key in FRONT_KEYS:                   # front matter titles (own page, exact line)
            i = find(key, 0, p0)
            if i is not None: pages[key] = roman(i + 1)
        else:
            i = find(key, p0, n)
            if i is not None: pages[key] = i - p0 + 1
    for kind, pre in (("fig", "Fig. "), ("tab", "Table ")):
        for no, _ in captions.get(kind, []):
            i = find(f"{pre}{no}:", p0, n)
            if i is not None: pages[f"{kind}:{no}"] = i - p0 + 1
    pages["_total_pdf_pages"] = n; pages["_front_pages"] = p0
    return pages


if __name__ == "__main__":
    template, out = sys.argv[1], sys.argv[2]
    work = os.path.join(os.path.dirname(os.path.abspath(out)), "_build"); os.makedirs(work, exist_ok=True)
    tmp = os.path.join(work, "pass.docx")
    caps = build(template, tmp, {}, {})
    caps = build(template, tmp, {}, caps)
    pdf = to_pdf(tmp, work)
    pages = compute_pages(pdf, caps)
    caps = build(template, out, pages, caps)
    pdf2 = to_pdf(out, work)
    pages2 = compute_pages(pdf2, caps)
    diff = {k: (pages.get(k), v) for k, v in pages2.items() if pages.get(k) != v and not k.startswith("_")}
    print("pages in final pdf:", pages2["_total_pdf_pages"], "| front matter pages:", pages2["_front_pages"], "| page-number mismatches:", diff or "none")
    json.dump(pages2, open(os.path.join(work, "pages.json"), "w"), indent=1)
    shutil.copy(pdf2, out.replace(".docx", ".pdf"))
