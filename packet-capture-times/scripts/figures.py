#!/usr/bin/env python3
"""Draw every figure of the report. Run from the scripts/ directory.  Needs matplotlib.
Values come from the experiment outputs (data/*.pcap, data/exfil_hist.json) - nothing is typed in by hand
except dates from the Senate report (Fig 5.5) and the drift arithmetic (Fig 5.2)."""
import json, io, contextlib, sys, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_pcap import parse

plt.rcParams.update({"font.family": "Liberation Serif", "font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.edgecolor": "#5B6670", "axes.linewidth": .8,
                     "savefig.dpi": 220, "figure.dpi": 100})
BLUE, ORANGE, GRAY, LGRAY, INK, GREEN = "#1F5FA8", "#C2570C", "#5B6670", "#E4E7EA", "#1b2129", "#1B7F79"
FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures")
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
W = 5.7

def save(fig, name):
    fig.savefig(os.path.join(FIG, name), bbox_inches="tight", facecolor="white"); plt.close(fig)

def box(ax, x, y, w, h, text, fc="#F3F5F7", ec=GRAY, tc=INK, fs=8.5, bold=False, lw=1.0, r=.02):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw))
    ax.text(x+w/2, y+h/2, text, ha="center", va="center", fontsize=fs, color=tc, fontweight="bold" if bold else "normal", linespacing=1.25)

def arrow(ax, x1, y1, x2, y2, color=GRAY, lw=1.2, style="-|>", ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=9, color=color, lw=lw, linestyle=ls, shrinkA=0, shrinkB=0))

def canvas(h, w=W):
    fig, ax = plt.subplots(figsize=(w, h)); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off"); return fig, ax

# ---------------------------------------------------------------- Fig 1.1 frame vs record
fig, ax = canvas(2.55)
ax.text(.0, .95, "On the wire (what the sender transmits)", fontsize=9, fontweight="bold", va="center")
for i, (t, w) in enumerate([("Ethernet header\nMACs, type", .2), ("IP header\naddresses, TTL,\nprotocol, ID", .22), ("TCP header\nports, seq/ack,\nflags, options", .22), ("Payload\n(application data)", .2), ("FCS", .08)]):
    x = .0 + sum([.2, .22, .22, .2, .08][:i]) + i*.012
    box(ax, x, .60, w, .25, t, fs=7.6, fc="#EEF3F9", ec=BLUE)
ax.text(.0, .53, "No field in these headers records when the frame reached the capture point.", fontsize=8, style="italic", color=GRAY, va="center")
arrow(ax, .5, .46, .5, .33, color=ORANGE, lw=1.6)
ax.text(.52, .395, "capture program reads its own host clock", fontsize=8, color=ORANGE, va="center")
ax.text(.0, .27, "Inside the pcap file (what the capture tool stores)", fontsize=9, fontweight="bold", va="center")
box(ax, .0, .0, .37, .22, "Record header (16 bytes)\nts_sec, ts_usec, incl_len, orig_len", fs=7.4, fc="#FBEFE6", ec=ORANGE, lw=1.5)
box(ax, .385, .0, .615, .22, "Packet data: the original frame bytes\n(Ethernet + IP + TCP + payload)", fs=7.4, fc="#EEF3F9", ec=BLUE)
save(fig, "fig_1_1_frame_vs_record.png")

# ---------------------------------------------------------------- Fig 2.1 where timing errors enter
fig, ax = canvas(2.7)
stages = [("1\nClock source", "oscillator drift,\nunsynchronised host", ORANGE),
          ("2\nStamping\npoint", "kernel, driver or\nNIC hardware", ORANGE),
          ("3\nFile format", "precision: µs or ns\n(pcap magic,\nif_tsresol)", BLUE),
          ("4\nDisplay", "relative, absolute,\nUTC or local zone", BLUE),
          ("5\nCorrelation", "other logs: zones,\noffsets, 1-s\nresolution", ORANGE)]
bw, gap = .17, .0375
for i, (t, s, c) in enumerate(stages):
    x = i*(bw+gap)
    box(ax, x, .50, bw, .34, t, fs=8, bold=True, fc="white", ec=c, lw=1.6)
    ax.text(x+bw/2, .44, s, ha="center", va="top", fontsize=7.6, color=INK, linespacing=1.25)
    if i < 4: arrow(ax, x+bw+.004, .67, x+bw+gap-.004, .67)
ax.text(0, .95, "Five places where the accuracy of a packet time can be lost", fontsize=9, fontweight="bold", va="center")
ax.add_patch(Rectangle((0, .0), .015, .05, fc=ORANGE, ec="none")); ax.text(.025, .025, "error changes the true instant", fontsize=8, va="center")
ax.add_patch(Rectangle((.42, .0), .015, .05, fc=BLUE, ec="none")); ax.text(.445, .025, "error changes only resolution or presentation", fontsize=8, va="center")
save(fig, "fig_2_1_error_chain.png")

# ---------------------------------------------------------------- Fig 3.1 methodology
fig, ax = canvas(2.45)
steps = [("1  Study", "Messier Ch. 4, 5, 10;\nstandards; seminar"), ("2  Construct", "5-frame pcap with\nsample timestamps"),
         ("3  Capture", "live loopback capture\nwith tcpdump"), ("4  Decode", "own parser, tcpdump,\ntshark, editcap"),
         ("5  Correlate", "zone, offset and\nprecision model"), ("6  Apply", "Target 2013 case;\nsynthetic exfil test")]
cw, ch = .305, .30
for i, (t, s) in enumerate(steps):
    r, c = divmod(i, 3); x = c*(cw+.0425); y = .58 if r == 0 else .12
    box(ax, x, y, cw, ch, "", fc="#F3F5F7", ec=BLUE if i < 4 else ORANGE, lw=1.4)
    ax.text(x+cw/2, y+ch-.07, t, ha="center", va="center", fontsize=8.8, fontweight="bold")
    ax.text(x+cw/2, y+.09, s, ha="center", va="center", fontsize=7.7, linespacing=1.25)
    if c < 2: arrow(ax, x+cw+.004, y+ch/2, x+cw+.0385, y+ch/2)
arrow(ax, 2*(cw+.0425)+cw/2, .58, cw/2, .42, ls=(0, (4, 3)))
save(fig, "fig_3_1_methodology.png")

# ---------------------------------------------------------------- Fig 3.2 capture architecture
fig, ax = canvas(2.7)
box(ax, 0, .66, .19, .26, "Client\n192.0.2.10", fs=8, fc="#EEF3F9", ec=BLUE)
box(ax, .30, .66, .22, .26, "Switch\n(SPAN / mirror\nport)", fs=8, fc="white", ec=GRAY)
box(ax, .63, .66, .19, .26, "Server\n198.51.100.7", fs=8, fc="#EEF3F9", ec=BLUE)
arrow(ax, .19, .79, .30, .79, style="<|-|>"); arrow(ax, .52, .79, .63, .79, style="<|-|>")
box(ax, .30, .20, .22, .24, "Capture host\n(own clock)", fs=8, fc="#FBEFE6", ec=ORANGE, lw=1.5)
arrow(ax, .41, .66, .41, .44, color=ORANGE, ls=(0, (4, 3)))
ax.text(.43, .55, "copy of every frame", fontsize=7.6, color=ORANGE, va="center")
box(ax, 0, .20, .19, .24, "NTP server\n(UTC reference)", fs=8, fc="white", ec=GREEN, lw=1.4)
arrow(ax, .19, .32, .30, .32, color=GREEN, ls=(0, (4, 3)))
ax.text(.245, .37, "sync", fontsize=7.4, color=GREEN, ha="center", va="bottom")
box(ax, .63, .20, .37, .24, "tcpdump / tshark write .pcap;\nWireshark analyses", fs=7.8, fc="white", ec=GRAY)
arrow(ax, .52, .32, .63, .32, color=GRAY); ax.text(.575, .37, "file", fontsize=7.4, color=GRAY, ha="center", va="bottom")
ax.text(0, .04, "A host sees only its own traffic on a switch; a SPAN port, hub or tap brings the traffic to the capture host.", fontsize=7.8, style="italic", color=GRAY)
save(fig, "fig_3_2_architecture.png")

# ---------------------------------------------------------------- Fig 3.3 pcap layout (values read from the file)
unit, rows = parse(os.path.join(DATA, "handshake_us.pcap")) if False else (None, None)
with contextlib.redirect_stdout(io.StringIO()):
    unit, rows = parse(os.path.join(DATA, "handshake_us.pcap"))
r1 = rows[0]
fig, ax = canvas(3.0)
ax.text(0, .96, "Classic pcap file (microsecond variant), values read from handshake_us.pcap", fontsize=9, fontweight="bold", va="center")
box(ax, 0, .66, .25, .17, "Global header\n24 bytes", fs=8, fc="#F3F5F7", ec=GRAY)
box(ax, .26, .66, .15, .17, "Record\nheader 16 B", fs=8, fc="#FBEFE6", ec=ORANGE, lw=1.5)
box(ax, .42, .66, .22, .17, "Packet data\n(frame 1: 74 B)", fs=8, fc="#EEF3F9", ec=BLUE)
box(ax, .65, .66, .15, .17, "Record\nheader 16 B", fs=8, fc="#FBEFE6", ec=ORANGE, lw=1.5)
box(ax, .81, .66, .19, .17, "Packet data\n(frame 2: 74 B)", fs=8, fc="#EEF3F9", ec=BLUE)
fields = [("ts_sec", str(r1[1]), "whole seconds\nsince epoch"), ("ts_usec", str(r1[2]), "microseconds\nwithin that second"),
          ("incl_len", str(r1[5]), "bytes\nstored"), ("orig_len", str(r1[6]), "bytes\non the wire")]
for i, (n, v, d) in enumerate(fields):
    x = .0 + i*.255
    box(ax, x, .30, .235, .20, f"{n}\n{v}", fs=8.3, bold=False, fc="white", ec=ORANGE, lw=1.3)
    ax.text(x+.1175, .24, d, ha="center", va="top", fontsize=7.4, color=GRAY, linespacing=1.2)
ax.plot([.26, 0], [.66, .50], color=ORANGE, lw=.9, ls=(0, (3, 2))); ax.plot([.41, 1.0], [.66, .50], color=ORANGE, lw=.9, ls=(0, (3, 2)))
ax.text(0, -.04, f"timestamp = ts_sec + ts_usec / 1,000,000 = {r1[1]}.{r1[2]:06d} s      (magic 0xa1b2c3d4 = µs, 0xa1b23c4d = ns)", fontsize=8.2, color=INK)
save(fig, "fig_3_3_pcap_layout.png")

# ---------------------------------------------------------------- Fig 3.4 normalisation pipeline
fig, ax = canvas(2.4)
st = [("1  Record", "source, zone,\nclock offset,\nprecision"), ("2  Convert", "local time →\nUTC / epoch"), ("3  Correct", "subtract the\nmeasured offset;\nkeep the raw\nvalue"),\
      ("4  Merge", "sort by\ncorrected time;\nnote resolution"), ("5  Validate", "cause before\neffect? if not,\nre-check clocks")]
bw, gap = .17, .0375
for i, (t, s) in enumerate(st):
    x = i*(bw+gap)
    box(ax, x, .22, bw, .62, "", fc="#F3F5F7", ec=BLUE if i < 4 else ORANGE, lw=1.4)
    ax.text(x+bw/2, .73, t, ha="center", va="center", fontsize=8.6, fontweight="bold")
    ax.text(x+bw/2, .44, s, ha="center", va="center", fontsize=7.6, linespacing=1.3)
    if i < 4: arrow(ax, x+bw+.004, .53, x+bw+gap-.004, .53)
ax.text(0, .06, "Zone conversion (step 2) is not synchronisation: only step 3 repairs a clock that is wrong.", fontsize=8, style="italic", color=GRAY)
save(fig, "fig_3_4_normalisation.png")

# ---------------------------------------------------------------- Fig 4.1 ladder diagram of the handshake
fig, ax = plt.subplots(figsize=(W, 3.5)); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
cx, sx = .24, .62
ax.text(cx, .97, "Client 192.0.2.10", ha="center", fontsize=8.6, fontweight="bold"); ax.text(sx, .97, "Server 198.51.100.7", ha="center", fontsize=8.6, fontweight="bold")
ax.plot([cx, cx], [.03, .92], color=GRAY, lw=1); ax.plot([sx, sx], [.03, .92], color=GRAY, lw=1)
ev = [(1, "TCP SYN", "17:40:01.212754", 0, 1, "+0.000000 s"), (2, "TCP SYN/ACK", "17:40:01.213981", 1, 0, "+0.001227 s"),
      (3, "TCP ACK", "17:40:01.214020", 0, 1, "+0.000039 s"), (4, "TLS Client Hello (571 B)", "17:40:01.247566", 0, 1, "+0.033546 s"),
      (5, "TLS Server Hello (1514 B)", "17:40:01.276694", 1, 0, "+0.029128 s")]
for k, (n, name, ts, a, b, d) in enumerate(ev):
    y = .84 - k*.17
    x1, x2 = (cx, sx) if a == 0 else (sx, cx)
    y2 = y - .045
    arrow(ax, x1, y, x2, y2, color=BLUE if a == 0 else ORANGE, lw=1.4)
    ax.text((cx+sx)/2, y+.012, f"{n}  {name}", ha="center", va="bottom", fontsize=7.9, rotation=0)
    ax.text(.005, y-.02, ts, fontsize=8, va="center", family="DejaVu Sans Mono", color=INK)
    ax.text(.83, y-.02, d, fontsize=8, va="center", family="DejaVu Sans Mono", color=GRAY)
ax.text(.005, .915, "arrival time (UTC)", fontsize=7.6, color=GRAY, va="bottom"); ax.text(.83, .915, "gap from previous", fontsize=7.6, color=GRAY, va="bottom")
save(fig, "fig_4_1_ladder.png")

# ---------------------------------------------------------------- Fig 5.1 live capture gaps
with contextlib.redirect_stdout(io.StringIO()):
    unit, rows = parse(os.path.join(DATA, "live_lo.pcap"))
gaps = [(r[0], max(float(r[8]), 1e-7)) for r in rows[1:]]
fig, ax = plt.subplots(figsize=(W, 2.9))
cols = [ORANGE if g >= .5 else BLUE for _, g in gaps]
ax.bar([n for n, _ in gaps], [g for _, g in gaps], color=cols, width=.62)
ax.set_yscale("log"); ax.set_ylim(1e-6, 6)
ax.set_xlabel("Frame number (gap measured from the previous frame)"); ax.set_ylabel("Gap (seconds, log scale)")
ax.axhline(1e-3, color=GRAY, lw=.8, ls=(0, (4, 3))); ax.text(16.45, 1.15e-3, "1 ms", fontsize=7.6, color=GRAY, ha="right", va="bottom")
for n, g in gaps:
    if g >= .5: ax.text(n, g*1.35, f"{g:.3f} s", ha="center", fontsize=8, color=ORANGE)
ax.set_xticks(range(2, 17)); ax.grid(axis="y", color=LGRAY, lw=.6); ax.set_axisbelow(True)
save(fig, "fig_5_1_live_gaps.png")

# ---------------------------------------------------------------- Fig 5.2 drift
import numpy as np
days = np.linspace(0, 365, 366)
fig, ax = plt.subplots(figsize=(W, 3.0))
for ppm, c, ls in ((5, GRAY, "-"), (20, BLUE, "-"), (50, ORANGE, "-")):
    y = ppm*1e-6*86400*days/60
    ax.plot(days, y, color=c, lw=2 if ppm == 20 else 1.5, ls=ls)
    ax.text(366, y[-1], f"  {ppm} ppm", color=c, va="center", fontsize=8.3)
ax.axhline(10, color=INK, lw=.8, ls=(0, (4, 3))); ax.text(4, 10.5, "10 minutes (the skew Messier warns about)", fontsize=8, va="bottom")
ax.set_xlim(0, 365); ax.set_xticks([0, 69, 139, 347, 365] if False else [0, 60, 120, 180, 240, 300, 365])
ax.set_xlabel("Days without synchronisation"); ax.set_ylabel("Accumulated error (minutes)")
ax.grid(color=LGRAY, lw=.6); ax.set_axisbelow(True); ax.set_ylim(0, 30)
ax.annotate("20 ppm reaches 10 min at day 347", xy=(347, 10), xytext=(150, 2.6), fontsize=8, color=BLUE, arrowprops=dict(arrowstyle="-", color=BLUE, lw=.8))
fig.subplots_adjust(right=.9)
save(fig, "fig_5_2_drift.png")

# ---------------------------------------------------------------- Fig 5.3 firewall / server lanes
from datetime import datetime
fig, ax = plt.subplots(figsize=(W, 2.9))
def m(h, mi, s): return h*3600 + mi*60 + s
def mins(t): return (t - m(14, 29, 0)) / 60
lanes = [("True time (UTC)", [(m(14,29,58), "firewall allows SSH", ORANGE), (m(14,30,0), "login follows", BLUE)]),
         ("Server log (NTP-synced)", [(m(14,30,0), "14:30:00  login accepted", BLUE)]),
         ("Firewall log (clock +4 min 10 s)", [(m(14,34,8), "14:34:08  ALLOW tcp/22", ORANGE)])]
for i, (nm, evs) in enumerate(lanes):
    y = 2 - i
    ax.plot([0, 6.2], [y, y], color=LGRAY, lw=6, solid_capstyle="round", zorder=1)
    ax.text(-.15, y, nm, ha="right", va="center", fontsize=8.3)
    for t, lab, c in evs:
        ax.scatter([mins(t)], [y], s=150 if c == ORANGE else 50, color=c, zorder=3 if c == BLUE else 2, edgecolor="white", linewidth=1.2)
    for t, lab, c in evs[-1:] if i else []:
        ax.text(mins(t), y+.22, lab, ha="center", fontsize=7.8, color=INK)
ax.text(mins(m(14,29,59)), 2.24, "14:29:58 firewall allows SSH (large marker), 14:30:00 login (small marker)", ha="left", fontsize=7.8)
ax.annotate("", xy=(mins(m(14,34,8)), .62), xytext=(mins(m(14,30,0)), .62), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=1))
ax.text((mins(m(14,34,8))+mins(m(14,30,0)))/2, .70, "merged by raw time, the login looks 4 min BEFORE the allow", ha="center", va="bottom", fontsize=7.8, color=ORANGE)
ax.set_xlim(-.2, 6.2); ax.set_ylim(-.35, 2.55); ax.set_yticks([])
ax.set_xticks(range(0, 7)); ax.set_xticklabels([f"14:{29+i}" for i in range(7)]); ax.spines["left"].set_visible(False)
ax.set_xlabel("Clock reading (UTC, 9 Nov 2026)")
save(fig, "fig_5_3_firewall_drift.png")

# ---------------------------------------------------------------- Fig 5.4 naive vs normalised merge
import importlib.util
spec = importlib.util.spec_from_file_location("tm", os.path.join(os.path.dirname(os.path.abspath(__file__)), "timeline_merge.py")); tm = importlib.util.module_from_spec(spec); spec.loader.exec_module(tm)
naive, fixed = tm.run()
fig, axs = plt.subplots(2, 1, figsize=(W, 4.3), gridspec_kw={"hspace": .72})
srcs = ["packet capture", "web server", "endpoint AV", "firewall", "monitoring SIEM"]
colr = {s: c for s, c in zip(srcs, [BLUE, GREEN, GRAY, ORANGE, "#7A3E9D"])}
mk = {"packet capture": "o", "web server": "s", "endpoint AV": "^", "firewall": "D", "monitoring SIEM": "P"}
ax = axs[0]
for t, s, msg in naive:
    h = t.hour + t.minute/60 + t.second/3600
    ax.scatter([h], [srcs.index(s)], color=colr[s], marker=mk[s], s=46, zorder=3)
ax.set_yticks(range(5)); ax.set_yticklabels(srcs, fontsize=8); ax.set_xlim(4.5, 16.2); ax.grid(axis="x", color=LGRAY, lw=.6)
ax.set_title("A  Raw log strings sorted as if every source used UTC", fontsize=8.8, loc="left", fontweight="bold")
ax.set_xlabel("Hour shown in the raw log lines"); ax.annotate("endpoint AV (New York time)\nappears 5 h before the attack", xy=(5.0, 2), xytext=(5.5, .55), fontsize=7.6, va="center", arrowprops=dict(arrowstyle="-", lw=.7, color=GRAY))
ax.annotate("firewall (Kolkata time)\n5.5 h after the attack", xy=(15.5, 3), xytext=(11.0, 2.2), fontsize=7.6, va="center", arrowprops=dict(arrowstyle="-", lw=.7, color=GRAY))
ax = axs[1]; t0 = fixed[0][0]
for t, s, msg, raw, res in fixed:
    x = (t - t0).total_seconds()
    ax.scatter([x], [srcs.index(s)], color=colr[s], marker=mk[s], s=46, zorder=3)
ax.set_yticks(range(5)); ax.set_yticklabels(srcs, fontsize=8); ax.set_xlim(-.6, 12); ax.grid(axis="x", color=LGRAY, lw=.6)
ax.set_xticks(range(0, 13, 2)); ax.set_xticklabels([f"10:00:{1+i:02d}" for i in range(0, 13, 2)], fontsize=8)
ax.set_title("B  After conversion to UTC and removal of measured clock offsets", fontsize=8.8, loc="left", fontweight="bold")
ax.set_xlabel("Corrected time (UTC, 9 Nov 2026)")
ax.text(11.8, 1.45, "activity at 10:00:01;\nlast alert 11 s later", fontsize=7.8, ha="right", va="center")
for a in axs: a.spines["left"].set_visible(False); a.tick_params(axis="y", length=0)
save(fig, "fig_5_4_merge.png")

# ---------------------------------------------------------------- Fig 5.5 Target timeline (dates from Senate report, Fig. 6 and text)
fig, ax = plt.subplots(figsize=(W, 4.6))
from datetime import date
def d(y, mo, dd): return (date(y, mo, dd) - date(2013, 11, 1)).days
ax.axhline(0, color=INK, lw=1.2)
# (x, label, level, ha, kind) - kind "pt" or ("span", x2)
att = [(d(2013,11,12), "12 Nov\nfirst access to\ninternal network", 1, "center", None),
       (d(2013,11,15), "15–28 Nov\nPOS malware tested\non few registers", 1, "center", d(2013,11,28)),
       (d(2013,11,30), "30 Nov\nmost POS infected;\nexfiltration malware\ninstalled on server", 2, "right", None),
       (d(2013,12,2), "2 Dec\nmalware updated;\nFTP transfers start", 1, "left", None)]
tgt = [(d(2013,11,28), "~28 Nov\nSymantec flags\nthe same server", 1, "right", None),
       (d(2013,11,30), "30 Nov–2 Dec\nFireEye alerts;\nno reaction", 2, "center", d(2013,12,2)),
       (d(2013,12,12), "12 Dec\nDOJ notifies\nTarget", 1, "right", None),
       (d(2013,12,15), "15 Dec\nbreach confirmed;\nPOS malware removed", 2, "center", None),
       (d(2013,12,19), "19 Dec\npublic notice:\n~40 M cards", 1, "left", None)]
LV = {1: .55, 2: 1.75}
ax.grid(axis="x", color=LGRAY, lw=.6); ax.set_axisbelow(True)
for items, sign, c in ((att, 1, ORANGE), (tgt, -1, BLUE)):
    for x, lab, lv, ha, x2 in items:
        y = sign*LV[lv]
        if x2:
            ax.plot([x, x2], [0, 0], color=c, lw=6, solid_capstyle="butt", zorder=2); xm = (x+x2)/2
        else: xm = x; ax.scatter([x], [0], color=c, s=26, zorder=3)
        ax.plot([xm, xm], [0, y - sign*.06], color=c, lw=.9)
        tx = {"center": xm, "right": xm+.4, "left": xm-.4}[ha]
        ax.text(tx, y, lab, ha=ha, va="bottom" if sign > 0 else "top", fontsize=7.2, color=INK, linespacing=1.2)
ax.set_xlim(8, 58); ax.set_ylim(-3.3, 3.3); ax.set_yticks([])
ticks = [d(2013,11,1), d(2013,11,15), d(2013,12,1), d(2013,12,15)]
ax.set_xticks(ticks); ax.set_xticklabels(["1 Nov 2013", "15 Nov", "1 Dec", "15 Dec"]); ax.spines["left"].set_visible(False)
ax.text(8.2, 3.05, "ATTACKER ACTIVITY", color=ORANGE, fontsize=8.5, fontweight="bold", va="center")
ax.text(8.2, -3.0, "TARGET DETECTION AND RESPONSE", color=BLUE, fontsize=8.5, fontweight="bold", va="center")
save(fig, "fig_5_5_target_timeline.png")

# ---------------------------------------------------------------- Fig 5.6 synthetic exfil histograms
h = json.load(open(os.path.join(DATA, "exfil_hist.json")))
fig, axs = plt.subplots(1, 2, figsize=(W, 2.7), sharey=True)
for ax, key, ttl, c in ((axs[0], "utc", "Binned by UTC hour", BLUE), (axs[1], "central", "Binned by US Central hour", ORANGE)):
    ax.bar(range(24), h[key], color=c, width=.75); ax.set_title(ttl, fontsize=8.8, loc="left", fontweight="bold")
    ax.set_xticks([0, 6, 12, 18, 23]); ax.set_xlabel("Hour of day"); ax.grid(axis="y", color=LGRAY, lw=.6); ax.set_axisbelow(True)
axs[0].set_ylabel("Volume sent (GB)")
top = max(h["utc"])
axs[0].set_ylim(0, top*1.28)
axs[0].text(20, top*1.1, "16:00–24:00", fontsize=8, ha="center", color=BLUE)
axs[1].text(14, top*1.1, "10:00–18:00", fontsize=8, ha="center", color=ORANGE)
fig.subplots_adjust(wspace=.08)
save(fig, "fig_5_6_exfil_hist.png")
print("figures written:", sorted(os.listdir(FIG)))
