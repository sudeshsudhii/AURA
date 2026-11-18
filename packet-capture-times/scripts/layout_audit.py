#!/usr/bin/env python3
"""Layout audit of the generated report: checks the rendered PDF against the intended layout.
Usage: python3 layout_audit.py report.docx report.pdf
Checks (all pages): margins/overflow, centring of centred paragraphs, images and page numbers,
headings/table captions stranded at a page bottom, page-number sequence; docx: indents and table widths."""
import re, subprocess, sys, html
import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH

PT = 72.0
PAGE_W = 595.3
TOL = 2.5          # points

def roman(n):
    s = ""
    for v, r in [(10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]:
        while n >= v: s += r; n -= v
    return s

def pdf_lines(pdf):
    out = subprocess.run(["pdftotext", "-bbox-layout", pdf, "-"], capture_output=True, text=True).stdout
    pages = []
    for pg in re.findall(r"<page[^>]*>(.*?)</page>", out, re.S):
        lines = []
        for ln in re.findall(r"<line ([^>]*)>(.*?)</line>", pg, re.S):
            a = dict(re.findall(r'(\w+)="([\d.]+)"', ln[0]))
            wb = re.findall(r'<word xMin="([\d.]+)" yMin="[\d.]+" xMax="([\d.]+)"[^>]*>(.*?)</word>', ln[1])
            words = [w[2] for w in wb]
            lines.append(dict(x0=float(a["xMin"]), x1=float(a["xMax"]), y0=float(a["yMin"]), y1=float(a["yMax"]),
                              t=html.unescape(" ".join(words)), w=[(float(x0), float(x1)) for x0, x1, _ in wb]))
        lines.sort(key=lambda l: (round(l["y0"]), l["x0"]))
        pages.append(lines)
    return pages

def pdf_images(pdf):
    out = subprocess.run(["pdftohtml", "-xml", "-zoom", "1", "-stdout", "-q", pdf], capture_output=True, text=True).stdout
    imgs = {}
    for pnum, body in re.findall(r'<page number="(\d+)"[^>]*>(.*?)</page>', out, re.S):
        for a in re.findall(r"<image ([^>]*)/>", body):
            d = dict(re.findall(r'(\w+)="([\d.]+)"', a))
            imgs.setdefault(int(pnum) - 1, []).append((float(d["left"]), float(d["left"]) + float(d["width"]), float(d["top"])))
    return imgs

def main(docx_path, pdf):
    issues = []
    d = docx.Document(docx_path)
    s0 = d.sections[0]
    cover_l, cover_r = s0.left_margin.inches * PT, PAGE_W - s0.right_margin.inches * PT
    sb = d.sections[-1]
    L, R = sb.left_margin.inches * PT, PAGE_W - sb.right_margin.inches * PT
    pages, imgs = pdf_lines(pdf), pdf_images(pdf)
    n = len(pages)
    p0 = next(i for i, ls in enumerate(pages) if any(l["t"] == "CHAPTER 1" for l in ls))

    def bounds(i): return (cover_l, cover_r) if i == 0 else (L, R)

    # ---------------- 1. margins / overflow
    for i, ls in enumerate(pages):
        lo, hi = bounds(i)
        for l in ls:
            if l["x0"] < lo - TOL or l["x1"] > hi + TOL:
                issues.append(f"p{i+1}: text outside margins x={l['x0']:.0f}-{l['x1']:.0f} (allowed {lo:.0f}-{hi:.0f}): {l['t'][:50]!r}")
        for (x0, x1, y) in imgs.get(i, []):
            if x0 < lo - TOL or x1 > hi + TOL:
                issues.append(f"p{i+1}: image outside margins x={x0:.0f}-{x1:.0f}")

    # ---------------- 2. centred paragraphs (body paragraphs only, not table cells)
    centred = []
    for p in d.paragraphs:
        t = " ".join(p.text.split())
        if t and p.alignment == WD_ALIGN_PARAGRAPH.CENTER:
            centred.append(t)
    checked = 0
    for t in centred:
        key = t[:28]
        hits = []
        for i, ls in enumerate(pages):
            for l in ls:
                if l["t"].startswith(key) or (len(key) > 12 and key.startswith(l["t"][:28]) and len(l["t"]) >= 12):
                    hits.append((i, l))
        if not hits:
            continue
        # the same words can also appear elsewhere (e.g. a TOC entry); judge the occurrence closest to centre
        def off(h):
            lo, hi = bounds(h[0]); return (h[1]["x0"] + h[1]["x1"]) / 2 - (lo + hi) / 2
        i, l = min(hits, key=lambda h: abs(off(h)))
        checked += 1
        if abs(off((i, l))) > TOL:
            issues.append(f"p{i+1}: centred line off-centre by {off((i, l)):+.1f} pt: {l['t'][:50]!r}")

    # ---------------- 3. images centred
    for i, lst in imgs.items():
        lo, hi = bounds(i)
        for (x0, x1, y) in lst:
            if i in (1,):            # bonafide logo is centred too after the fix
                pass
            c = (x0 + x1) / 2
            if abs(c - (lo + hi) / 2) > TOL + 1:
                issues.append(f"p{i+1}: image off-centre by {c - (lo + hi) / 2:+.1f} pt (x {x0:.0f}-{x1:.0f})")

    # ---------------- 4. page numbers: position and sequence
    for i, ls in enumerate(pages):
        if i == 0: continue
        foot = [l for l in ls if l["y0"] > 841.9 - 72 and re.fullmatch(r"[ivx]+|\d+", l["t"])]
        want = roman(i + 1) if i < p0 else str(i - p0 + 1)
        if not foot:
            issues.append(f"p{i+1}: no page number found (expected {want})"); continue
        f = foot[-1]
        if f["t"] != want: issues.append(f"p{i+1}: page number {f['t']!r}, expected {want!r}")
        c = (f["x0"] + f["x1"]) / 2
        if abs(c - (L + R) / 2) > TOL: issues.append(f"p{i+1}: page number off-centre by {c - (L + R) / 2:+.1f} pt")

    # ---------------- 5. stranded headings / table captions at the bottom of a page
    heads = [" ".join(p.text.split()) for p in d.paragraphs if p.style.name in ("Heading 2", "Heading 3") and p.text.strip()]   # Heading 1 is centred by design
    for i, ls in enumerate(pages):
        body = [l for l in ls if l["y0"] < 841.9 - 72]
        if not body: continue
        last = body[-1]["t"]
        if any(last.startswith(h[:30]) for h in heads) or re.match(r"Table [\dA-Z]+\.\d+:", last):
            issues.append(f"p{i+1}: '{last[:50]}' is the last line on the page (stranded)")

    # ---------------- 6. headings start at the left margin
    for i, ls in enumerate(pages[p0:], start=p0):
        for l in ls:
            if any(l["t"] == h for h in heads) and abs(l["x0"] - L) > TOL:
                issues.append(f"p{i+1}: heading not at left margin (x={l['x0']:.0f}): {l['t'][:40]!r}")

    # ---------------- 6a. blank pages (nothing but a page number)
    for i, ls in enumerate(pages):
        body_lines = [l for l in ls if not re.fullmatch(r"[ivx]+|\d+", l["t"])]
        if not body_lines and not imgs.get(i):
            issues.append(f"p{i+1}: blank page")

    # ---------------- 6b. cover: names evenly and compactly spaced; no wrapped centred lines except the title
    cov = pages[0]
    from_names = [l for l in cov if re.search(r"\[RA\d{13}\]", l["t"])]
    gaps = [round(b["y0"] - a["y1"], 1) for a, b in zip(from_names, from_names[1:])]
    if gaps and (max(gaps) - min(gaps) > 1 or max(gaps) > 8):
        issues.append(f"p1: student-name lines unevenly or loosely spaced, gaps {gaps} pt")
    for a_, b_ in zip(cov, cov[1:]):
        # a wrapped centred paragraph shows as a full-width line followed by a short line with a tiny gap
        if (a_["x1"] - a_["x0"]) > 0.92 * (cover_r - cover_l) and b_["y0"] - a_["y1"] < 6 and not a_["t"].isupper():
            issues.append(f"p1: centred line wraps: {a_['t'][:45]!r} / {b_['t'][:30]!r}")

    # ---------------- 6c. stretched justified lines: rebuild visual rows from words (pdftotext splits a row at big gaps)
    import statistics
    for i, ls in enumerate(pages[1:], start=1):
        words = sorted(((w0, w1, round(l["y0"])) for l in ls for (w0, w1) in l["w"]), key=lambda w: (w[2], w[0]))
        rows = {}
        for w0, w1, y in words:
            key = next((k for k in rows if abs(k - y) <= 1.5), y); rows.setdefault(key, []).append((w0, w1))
        for y, ws in rows.items():
            ws.sort()
            if len(ws) < 4 or not (L - 1.5 < ws[0][0] < L + 40) or abs(ws[-1][1] - R) > 1.5: continue
            gaps = [b[0] - a_[1] for a_, b in zip(ws, ws[1:])]
            if statistics.median(gaps) >= 9:     # normal justified spacing is ~3-7 pt
                txt = next((l["t"] for l in ls if abs(round(l["y0"]) - y) <= 1.5), "")
                issues.append(f"p{i+1}: stretched justified line (median word gap {statistics.median(gaps):.0f} pt): {txt[:55]!r}")

    # ---------------- 6d. alignment consistency of body paragraphs (docx)
    in_chapters = False
    for p in d.paragraphs:
        t = p.text.strip()
        if t.startswith("CHAPTER 1"): in_chapters = True
        if t == "REFERENCES": in_chapters = False
        if not in_chapters or not t or p.style.name.startswith("Heading"): continue
        al = p.alignment
        mono = p.runs and all((r.font.name or "").startswith("Courier") for r in p.runs if r.text.strip())   # whole-line code only
        if mono or al == WD_ALIGN_PARAGRAPH.CENTER: continue      # code lines, captions, figures
        if al != WD_ALIGN_PARAGRAPH.JUSTIFY:
            issues.append(f"docx: body paragraph not justified ({al}): {t[:50]!r}")

    # ---------------- 7. docx: unexpected indents, table widths
    ok_ind = {(0.0, 0.0), (0.25, -0.25), (0.46, -0.46), (0.3, -0.3), (0.0, 0.4), (2.93, 0.0)}
    for p in d.paragraphs:
        pf = p.paragraph_format
        li = round((pf.left_indent or 0) / 914400, 2); fi = round((pf.first_line_indent or 0) / 914400, 2)
        ri = round((pf.right_indent or 0) / 914400, 2)
        if p.text.strip() and ((li, fi) not in ok_ind or ri not in (0.0, 0.1)):
            issues.append(f"docx: unusual indent left={li} first={fi} right={ri}: {p.text[:50]!r}")
    W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    text_w = (sb.page_width - sb.left_margin - sb.right_margin) / 914400
    for k, t in enumerate(d.tables):
        tw = t._tbl.tblPr.find(W + "tblW")
        w = int(tw.get(W + "w")) / 1440 if tw is not None and tw.get(W + "type") == "dxa" else None
        grid = sum(int(g.get(W + "w")) for g in t._tbl.find(W + "tblGrid").findall(W + "gridCol")) / 1440
        if w is None or w > text_w + 0.02 or abs(grid - w) > 0.02:
            issues.append(f"docx: table {k} width {w} / grid {grid:.2f} in (text width {text_w:.2f}): {t.rows[0].cells[0].text[:30]!r}")

    print(f"pages: {n} (front matter {p0}), centred paragraphs checked: {checked}, images: {sum(len(v) for v in imgs.values())}")
    print(f"ISSUES: {len(issues)}")
    for s in issues: print("  -", s)
    return issues

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
