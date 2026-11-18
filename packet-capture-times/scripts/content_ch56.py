"""Chapters 5, 6, references and appendices."""
from docx.enum.text import WD_ALIGN_PARAGRAPH as AL

C, L = AL.CENTER, AL.LEFT

REFERENCES = [
    "R. Messier, *Network Forensics*. Indianapolis, IN, USA: Wiley, 2017, ISBN: 978-1-119-32828-5. Ch. 4, “Packet Capture and Analysis”; Ch. 5, “Attack Types”; Ch. 10, “Correlating Attacks”.",
    "U.S. Senate Committee on Commerce, Science, and Transportation, Majority Staff, “A ‘Kill Chain’ Analysis of the 2013 Target Data Breach,” Staff Report, Washington, DC, USA, Mar. 26, 2014.",
    "J. Mulligan, “Written testimony,” in *Privacy in the Digital Age: Preventing Data Breaches and Combating Cybercrime*, U.S. Senate Committee on the Judiciary, Washington, DC, USA, Feb. 4, 2014.",
    "The Tcpdump Group, “pcap-savefile(5): libpcap savefile format,” manual page, tcpdump.org / man7.org.",
    "The Tcpdump Group, “tcpdump(1): dump traffic on a network,” manual page, tcpdump.org. [Online]. Available: https://www.tcpdump.org/manpages/tcpdump.1.html",
    "Wireshark Foundation, “Wireshark User’s Guide: Time Display Formats and Time References.” [Online]. Available: https://www.wireshark.org/docs/",
    "IETF OPSAWG, “PCAP Next Generation (pcapng) Capture File Format,” Internet-Draft, draft-ietf-opsawg-pcapng (work in progress; check the current revision).",
    "D. Mills, J. Martin, J. Burbank, and W. Kasch, “Network Time Protocol Version 4: Protocol and Algorithms Specification,” IETF RFC 5905, Jun. 2010.",
    "K. Kent, S. Chevalier, T. Grance, and H. Dang, “Guide to Integrating Forensic Techniques into Incident Response,” NIST Special Publication 800-86, Aug. 2006.",
    "K. Kent and M. Souppaya, “Guide to Computer Security Log Management,” NIST Special Publication 800-92, Sep. 2006.",
    "D. Borman, B. Braden, V. Jacobson, and R. Scheffenegger, “TCP Extensions for High Performance,” IETF RFC 7323, Sep. 2014.",
    "M. W. Stevens, “Unification of relative time frames for digital forensics,” *Digital Investigation*, vol. 1, no. 3, pp. 225–239, Sep. 2004, doi: 10.1016/j.diin.2004.07.003.",
    "M. C. Weil, “Dynamic time & date stamp analysis,” *International Journal of Digital Evidence*, vol. 1, no. 2, Summer 2002.",
    "J. Olsson and M. Boldt, “Computer forensic timeline visualization tool,” *Digital Investigation*, vol. 6, pp. S78–S87, 2009, doi: 10.1016/j.diin.2009.06.008.",
    "C. Hargreaves and J. Patterson, “An automated timeline reconstruction approach for digital forensic investigations,” *Digital Investigation*, vol. 9, pp. S69–S79, 2012, doi: 10.1016/j.diin.2012.05.006.",
    "E. M. Hutchins, M. J. Cloppert, and R. M. Amin, “Intelligence-driven computer network defense informed by analysis of adversary campaigns and intrusion kill chains,” Lockheed Martin Corporation, 2011.",
    "GitHub Engineering, “February 28th DDoS Incident Report,” GitHub blog, Mar. 1, 2018. [Online]. Available: https://github.blog",
    "The Open Group, “Base Definitions, Section 4.16: Seconds Since the Epoch,” in *The Open Group Base Specifications*, POSIX.1-2017 (IEEE Std 1003.1-2017).",
]


def ch5(R):
    R.H1("Chapter 5: Results and Discussion")
    R.H2("5.1 Findings and Output")
    R.H3("5.1.1 The constructed capture agrees across three readers")
    R.P("All five timestamps of the constructed capture were read back correctly by the three independent readers. The parser parse_pcap.py, tcpdump and tshark gave the same arrival times, the same gaps (0.001227 s, 0.000039 s, 0.033546 s and 0.029128 s), the same time since the first frame (up to 0.063940 s for the fifth frame) and the same epoch values, including 1794246001.247566 for frame 4. The capture duration reported by capinfos was 0.063940 s, which equals the difference between the first and last timestamps, 17:40:01.276694 − 17:40:01.212754. The raw bytes of the record header contain exactly the integers 1794246001 and 212754 (Section 4.1.4), which confirms that the arrival time is file metadata and is not a field of the Ethernet, IP or TCP headers.")
    R.H3("5.1.2 The live capture separates machine speed from human speed")
    R.P("The live capture (D2) has 16 frames over 2.303306 s. Fig. 5.1 plots the gap before each frame on a logarithmic axis, and Table 5.1 counts the gaps by band. Twelve of the fifteen gaps are below a millisecond and range from 4 µs to 215 µs; they are the exchanges of the stack with itself on loopback. The SYN to SYN/ACK took 18 µs, and the whole three-way handshake was completed 31 µs after the first SYN. Two gaps stand out: 0.800260 s before frame 8 and 1.500237 s before frame 11. These are the two scripted pauses of 0.8 s and 1.5 s, so the capture reproduced the pauses to within 0.26 ms and 0.24 ms. A reader who knew nothing about the experiment could still tell from the gaps alone where a “person” paused.")
    R.FIG("5", "fig_5_1_live_gaps.png", "Live capture: gap before each frame (log scale); the two orange bars are scripted pauses")
    R.TABLE("5", "Gaps between consecutive frames of the live capture (kind: live)",
            ["Gap band", "Number of gaps", "Reading"],
            [["Below 1 ms", "12", "Machine-speed exchanges (4 µs to 215 µs)"],
             ["1 ms to 100 ms", "1", "Teardown: the FIN exchange (1.823 ms)"],
             ["100 ms to 0.5 s", "0", "None"],
             ["0.5 s or more", "2", "Pauses: 0.800260 s and 1.500237 s"]],
            [1.6, 1.3, 2.87], size=10, align=[L, C, L])
    R.P("The same capture shows why precision matters. Its 16 frames fall in only three wall-clock seconds: seven in 02:20:24, three in 02:20:25 and six in 02:20:27. A log with one-second resolution that wrote a line stamped 02:20:24 could not be ordered against any of those seven frames; they must be treated as simultaneous with that line, and the report must say so.")
    R.H3("5.1.3 Clock drift and its effect on ordering")
    R.P("Table 5.2 and Fig. 5.2 show the drift model. A clock that gains 20 ppm drifts by about 1.7 s a day and about 52 s in 30 days, and it reaches the ten-minute error that Messier warns about [1] after 347 days without synchronisation. A 50 ppm clock reaches it in 139 days. The numbers are small per day and large per year, which is why a machine that has not been synchronised for months is dangerous as evidence.")
    R.TABLE("5", "Accumulated error of a clock that runs fast by P ppm (computed by drift_model.py)",
            ["P (ppm)", "Per day (s)", "Per 30 days (s)", "Per year (s)", "Days to reach 10 min"],
            [["5", "0.432", "12.96", "157.7", "1389"], ["20", "1.728", "51.84", "630.7", "347"],
             ["50", "4.320", "129.60", "1576.8", "139"], ["100", "8.640", "259.20", "3153.6", "69"]],
            [0.9, 1.1, 1.3, 1.2, 1.27], size=10, align=[C, C, C, C, C])
    R.FIG("5", "fig_5_2_drift.png", "Accumulated clock error for 5, 20 and 50 ppm; the dashed line is ten minutes")
    R.P("Fig. 5.3 turns this into an ordering failure with the hypothetical example D4. In true time a firewall allowed an SSH connection at 14:29:58 and the server accepted the login at 14:30:00. The server clock is NTP-synchronised and wrote 14:30:00, but the firewall clock is 4 min 10 s fast and wrote 14:34:08. Merged by raw time, the login appears 4 min 8 s before the connection was allowed, which is impossible. Subtracting the measured offset restores the correct order, 14:29:58 and then 14:30:00. The lesson is to suspect the clocks before suspecting anything else when an impossible order appears.")
    R.FIG("5", "fig_5_3_firewall_drift.png", "Firewall and server logs: a 4 min 10 s offset reverses cause and effect (hypothetical)")
    R.H3("5.1.4 Normalisation restores the order of five sources")
    R.P("Fig. 5.4 and Table 5.3 show the result of the normalisation procedure on the hypothetical set D3. Sorted as raw strings, as if every source used the same zone and a perfect clock, the events appear in a scrambled order: the endpoint antivirus line (05:00:05, New York time) comes first, about five hours before the attack, and the firewall alert (15:30:12, Kolkata time) comes last, five and a half hours after it. After conversion to UTC and removal of the measured offsets, the events fall within 11 s: suspicious connection at 10:00:01, repeated requests at 10:00:03, upload at 10:00:03.420, outbound transfer at 10:00:05, quarantine at 10:00:07, firewall alert at 10:00:08 and SIEM alert at 10:00:12. The validation step confirmed that every alert is later than the first suspicious packet. The packets show the activity 7 s before the first alert and 11 s before the last, so alerts lag the traffic and an analyst who used the alert time alone would underestimate how long the attacker had been active.")
    R.FIG("5", "fig_5_4_merge.png", "Five sources before and after normalisation (hypothetical)")
    R.TABLE("5", "Order of events before and after normalisation (kind: hypothetical)",
            ["Source", "Raw log line", "Zone / offset", "Corrected time (UTC)", "Rank raw", "Rank corrected"],
            [["Packet capture", "10:00:01.000000", "UTC / none", "10:00:01.000", "2", "1"],
             ["Packet capture", "10:00:03.000000", "UTC / none", "10:00:03.000", "3", "2"],
             ["Web server", "10:00:03.420", "UTC / none", "10:00:03.420", "4", "3"],
             ["Packet capture", "10:00:05.000000", "UTC / none", "10:00:05.000", "5", "4"],
             ["Endpoint AV", "05:00:05", "New York / −2 s", "10:00:07", "1", "5"],
             ["Firewall", "15:30:12", "Kolkata / +4 s", "10:00:08", "7", "6"],
             ["Monitoring SIEM", "10:00:12", "UTC / none", "10:00:12", "6", "7"]],
            [1.2, 1.15, 1.05, 1.05, 0.65, 0.67], size=9, align=[L, C, L, C, C, C])
    R.H3("5.1.5 The Target breach timeline")
    R.P("Fig. 5.5 places the reported events of the Target breach on one axis, with the attacker’s actions above the line and Target’s detection and response below it. The attacker lane spans about two months, from the credential theft in September 2013 to mid-December. Inside Target’s network the activity runs from first access on 12 November 2013, tests of the point-of-sale malware on a few registers from 15 to 28 November, most registers infected and the exfiltration malware installed on a server by 30 November, and stolen data leaving by FTP from 2 December. Target’s detection lane has early signals: antivirus software flagged malicious behaviour on the same server around 28 November, and the FireEye system raised alerts with each installation of the exfiltration malware between 30 November and 2 December, but, according to the report, the security team did not react [2]. The Justice Department notified Target on 12 December, ten days after the last of those alerts; the breach was confirmed and the malware removed from virtually all registers on 15 December, and about 40 million card records were announced as exposed on 19 December [2], [3]. The dates are as reported and are not packet times. The timeline is possible only because events have trustworthy times, and the shape of the two lanes is the lesson: the early signals existed, but the response followed outside notification.")
    R.FIG("5", "fig_5_5_target_timeline.png", "Reported attack and response timeline of the Target breach, 2013 (dates as reported in [2], [3])", width=5.7)
    R.H3("5.1.6 A time-of-day analysis of exfiltration (synthetic)")
    R.P("The Senate report states that, according to an analysis by Dell SecureWorks, the exfiltration ran between 10 a.m. and 6 p.m. Central time, and that about 11 GB were collected over about two weeks [2]. To show how packet times would be used to find such a pattern, the script exfil_window.py generates synthetic outbound FTP session records (164 sessions, 11.00 GB, 2 to 15 December 2013) that follow the documented pattern, and then analyses them as an investigator would. The window matches the documented one by construction; the purpose of the test is to show how the result looks depending on the zone used to read the times. Binned by US Central hour, all of the volume falls between 10:00 and 18:00. Binned by UTC hour, the same sessions appear between 16:00 and 24:00 (Central Standard Time is UTC−6 in December). An analyst who read the capture in UTC and did not know the zone of the victim could wrongly describe the activity as an evening or night pattern (Fig. 5.6).")
    R.FIG("5", "fig_5_6_exfil_hist.png", "Synthetic outbound volume by hour of day: the same sessions in UTC and in US Central time")
    R.H2("5.2 Discussion")
    R.P("The results meet the objectives of Section 1.4. The origin and storage of the time were shown on a real file and confirmed by three readers (objective 1). The three display forms, relative, absolute and epoch, were compared for the same frame (objective 2). The effects of zones, drift and precision were quantified and a procedure was shown to correct them (objective 3). The Target timeline was built from reported dates, and the exfiltration test showed how zones affect the reading of a time-of-day pattern (objective 4). Practical recommendations follow in Section 5.3 (objective 5).")
    R.P("Four points deserve comment. First, the live capture confirms the standard teaching that a capture can distinguish automatic and human behaviour from gaps alone, but it also shows the limit: on loopback every machine exchange is a few tens of microseconds, so the capture says nothing about the delay of a real network path. Second, the precision problem is easy to underestimate: seven frames inside one second cannot be ordered against a single log line, and the alert-lag result of Section 5.1.4 is computed at one-second resolution for that reason. Third, converting the file to pcapng did not add precision. A format that can store more digits does not make the clock better. Fourth, the choice of display format can change a conclusion. Wireshark’s default relative time says nothing about the time of day, and the UTC and Central views of the same exfiltration data differ by six hours. Every time quoted in a report should therefore carry its reference and format, as requirement R4 states.")
    R.P("The results also depend on stated assumptions. The 20 ppm drift value illustrates an order of magnitude and is not a measurement. The event sets D3 and D4 and the exfiltration data D5 were built to demonstrate a method, so what they show is how the method behaves, not how often these situations occur. No claim is made that the Target attackers or defenders were affected by any particular clock fault.")
    R.H2("5.3 Practical Implications")
    R.P("Table 5.4 turns the findings into practices for an investigating team, and relates each one to the evidence of this study.")
    R.TABLE("5", "Recommended practices and the evidence behind each",
            ["Practice", "Why (evidence in this study)"],
            [["Synchronise every server, network device and endpoint with NTP", "A 20 ppm clock reaches ten minutes in 347 days (Table 5.2); one wrong clock reversed cause and effect (Fig. 5.3)"],
             ["Use UTC as the common reference and convert only for display", "Raw local strings scrambled five sources by up to 5.5 hours (Fig. 5.4); UTC and Central views differed by six hours (Fig. 5.6)"],
             ["Preserve the original capture, work on a copy, and hash it", "The time is metadata of the file (Section 4.1.4); any rewrite can change it"],
             ["Record the capture configuration and the capture host’s clock offset at collection time", "Offsets can be corrected only if they were measured (Section 4.2.3)"],
             ["State the precision and display format of every quoted time", "Seven frames share one second (Section 5.1.2); relative, absolute and epoch times answer different questions (Table 4.2)"],
             ["Place the capture sensor where the traffic is, using a SPAN port, hub or tap", "A host on a switch sees only its own frames [1]; the absence of traffic in a capture proves nothing if the sensor was in the wrong place"],
             ["Verify timestamps before correlating and check that the order is possible", "In the raw order the antivirus event preceded the attack by hours; only after correction did the validation step pass (Table 5.3)"]],
            [2.5, 3.27], size=9.5)
    R.P("For a case such as Target, the packet times of a real capture would be used to answer the questions of Table 5.5. The table is an illustration of method, as the data of the case are not available, and the commands use documentation addresses and a placeholder date. Every conclusion would also depend on the capture host’s clock being right.")
    R.TABLE("5", "How packet times would help to investigate a breach of the Target type (illustrative)",
            ["Investigative question", "How packet times help"],
            [["Suspicious internal traffic", "First-seen time of a vendor-portal host talking to point-of-sale or staging servers marks lateral movement"],
             ["Compromised systems", "A server that accepts connections from many registers in a repeating rhythm is a collection point"],
             ["Unusual outbound traffic", "Internal servers do not normally use FTP to outside hosts; packet times give the start, end and duration of each session"],
             ["Possible exfiltration", "Transfer volume per interval clustering in a daily window (Fig. 5.6); Wireshark’s Statistics, Conversations"],
             ["External destinations", "Earliest and latest packet to each outside address shows one-off or persistent contact"],
             ["Correlation with alerts", "Do packets from that host begin just before or after each alert time?"],
             ["Sequence of activity", "Merge into one timeline: foothold, staging, outbound transfers, detection"]],
            [1.8, 3.97], size=9.5)
    R.code("""# illustrative commands (documentation address, placeholder date)
# every FTP packet, with date and time
tcpdump -nn -tttt -r cap.pcap 'tcp port 21'
# first contact with an outside host
tcpdump -nn -tttt -r cap.pcap 'dst host 198.51.100.7' | head -1
# Wireshark display filter limited to a time window
ftp && frame.time >= 'YYYY-MM-DD 10:00:00'""")


def ch6(R):
    R.H1("Chapter 6: Conclusion and Future Scope")
    R.H2("6.1 Conclusion")
    R.P("This case study examined packet capture times in network forensics and used the 2013 Target breach as its real-world case. A packet does not carry its arrival time. The capture program reads its own host clock when it sees the frame and writes the value into the record header of the pcap file, as seconds since the epoch plus a microsecond or nanosecond fraction. A constructed five-frame capture was read identically by an independent parser, tcpdump 4.99.4 and tshark 4.2.2, and the raw bytes showed the values 1794246001 and 212754. A live capture showed machine-speed gaps of microseconds and two human-like pauses recorded to within a fraction of a millisecond.")
    R.P("Three conclusions follow. First, a packet time is a measurement with four sources of error, namely the clock, the stored precision, the display format and the comparison with other sources, and each must be controlled: NTP corrects the clock, UTC removes zone differences, the file’s magic number or if_tsresol sets the precision, and an explicit statement of the display format removes ambiguity. Second, merging evidence is a procedure and not a sort: record, convert, correct, merge and validate restored the order of five sources whose raw lines were scrambled by up to 5.5 hours and a few seconds of offset, and a 4 min 10 s offset was enough to reverse cause and effect. Third, in the Target case the attack and its early warning signs unfolded over weeks, and a time-of-day pattern such as the reported 10:00 to 18:00 Central window looks different in UTC; the reading of time therefore decides whether such a pattern is recognised.")
    R.H2("6.2 Future Scope")
    R.bullets([
        "**Real network captures.** Repeat the live capture on a physical network with a SPAN port or tap and compare the loopback gaps with real propagation and queueing delays, using several capture hosts to measure the disagreement between their clocks.",
        "**Clock-quality metadata.** Record NTP status (for example the offset and stratum reported by the time daemon) at the start and end of each capture, store it with the file, and use it to correct timestamps automatically.",
        "**Hardware timestamps.** Study captures stamped by the network card and synchronised with the Precision Time Protocol, and measure how much they improve on kernel timestamps.",
        "**Nanosecond workflows.** Extend the scripts to nanosecond pcap and pcapng files with different interface resolutions and to the comparison of files with mixed precision.",
        "**Automated offset estimation.** Estimate the offset between two sources from events known to occur together, for example a connection seen in both a firewall log and a capture, in the spirit of the clock-unification work of Stevens [12].",
        "**SIEM and timeline tools.** Feed the corrected events into Plaso or a SIEM and compare the automatically built timeline with the one of this study [1], [14], [15].",
        "**Public data sets.** Repeat the time-of-day analysis on a public capture or flow data set with a real exfiltration or beaconing pattern, instead of synthetic sessions."])


def refs_and_appendices(R, readme_tree):
    R.H1("References")
    for i, r in enumerate(REFERENCES, 1):
        p = R.doc.add_paragraph(); R._fmt(p, AL.JUSTIFY, 1.3, 6, indent=0.45, first=-0.45)
        R.runs(p, f"[{i}]\t" + r, 11)
        # tab stop
        from docx.shared import Inches
        p.paragraph_format.tab_stops.add_tab_stop(Inches(0.45))
    R.H1("Appendix A: Scripts")
    R.P("All scripts are in the scripts folder of the accompanying archive. The listing below shows the core of the capture builder and the parser; the remaining scripts are described in Table A.1.", after=4)
    R.H3("A.1 make_pcap.py (excerpt)")
    R.code("""T = 1794246001    # 2026-11-09 17:40:01 UTC
frames = [   # (seconds, microseconds, frame bytes)
 (T, 212754, frame(CLIENT, SERVER, ..., flags=0x02)),   # SYN
 (T, 213981, frame(SERVER, CLIENT, ..., flags=0x12)),   # SYN/ACK
 (T, 214020, frame(CLIENT, SERVER, ..., flags=0x10)),   # ACK
 (T, 247566, frame(CLIENT, SERVER, ..., payload=ch)),   # Client Hello
 (T, 276694, frame(SERVER, CLIENT, ..., payload=sh)),   # Server Hello
]
def write(path, nano=False):
    magic = 0xa1b23c4d if nano else 0xa1b2c3d4
    with open(path, "wb") as f:
        f.write(struct.pack("<IHHiIII",
                magic, 2, 4, 0, 0, 65535, 1))   # global header
        for s, us, fr in frames:
            frac = us * 1000 if nano else us
            f.write(struct.pack("<IIII",
                    s, frac, len(fr), len(fr)))  # record header
            f.write(fr)""", size=8)
    R.H3("A.2 parse_pcap.py (excerpt)")
    R.code("""magic = struct.unpack("<I", d[:4])[0]
unit = {0xa1b2c3d4: ("microsecond", 6), 0xa1b23c4d: ("nanosecond", 9)}[magic]
off = 24
while off < len(d):
    ts_sec, ts_frac, incl, orig = struct.unpack(
        "<IIII", d[off:off+16]); off += 16
    t = Decimal(ts_sec) + Decimal(ts_frac) / Decimal(10**unit[1])
    ...
    off += incl""", size=8)
    R.TABLE("A", "Scripts of the study", ["Script", "Purpose"],
            [["make_pcap.py", "Builds the constructed capture in microsecond and nanosecond forms"],
             ["parse_pcap.py", "Decodes global and record headers and prints exact times, relative times and gaps"],
             ["live_capture.sh", "Takes the live loopback capture with scripted pauses"],
             ["gap_analysis.py", "Classifies inter-frame gaps into bands"],
             ["timeline_merge.py", "Normalises and merges events from five sources"],
             ["drift_model.py", "Clock-drift table and the firewall and server example"],
             ["tz_table.py", "Zone table and epoch checks from the IANA database"],
             ["exfil_window.py", "Synthetic exfiltration sessions and their time-of-day analysis"],
             ["figures.py, report_lib.py, build_report.py", "Figures and the generation of this report"]],
            [2.2, 3.57], size=10)
    R.H1("Appendix B: Tool Output")
    R.P("Output of tshark for the constructed capture, with all four time fields of every frame (columns: frame number, time since first frame, gap from previous frame, epoch time, arrival time):", after=3)
    R.code("""1 0.000000000 0.000000000 1794246001.212754000 Nov  9, 2026 17:40:01.212754000 UTC
2 0.001227000 0.001227000 1794246001.213981000 Nov  9, 2026 17:40:01.213981000 UTC
3 0.001266000 0.000039000 1794246001.214020000 Nov  9, 2026 17:40:01.214020000 UTC
4 0.034812000 0.033546000 1794246001.247566000 Nov  9, 2026 17:40:01.247566000 UTC
5 0.063940000 0.029128000 1794246001.276694000 Nov  9, 2026 17:40:01.276694000 UTC""", size=7.5)
    R.P("Output of parse_pcap.py for the same file:", after=3)
    R.code(""" #     ts_sec   ts_frac          epoch (s)                 UTC  incl  orig  since 1st     delta
 1 1794246001    212754 1794246001.212754 2026-11-09 17:40:01    74    74   0.000000         0
 2 1794246001    213981 1794246001.213981 2026-11-09 17:40:01    74    74   0.001227  0.001227
 3 1794246001    214020 1794246001.214020 2026-11-09 17:40:01    66    66   0.001266  0.000039
 4 1794246001    247566 1794246001.247566 2026-11-09 17:40:01   571   571   0.034812  0.033546
 5 1794246001    276694 1794246001.276694 2026-11-09 17:40:01  1514  1514   0.063940  0.029128""", size=7)
    R.P("Output of gap_analysis.py for the live capture:", after=3)
    R.code("""16 frames, duration 2.303306 s
  < 1 ms             12
  1 ms - 100 ms       1
  100 ms - 0.5 s      0
  >= 0.5 s            2
largest gaps: frame 11: 1.500237 s, frame 8: 0.800260 s, frame 15: 0.001823 s
SYN -> SYN/ACK : 18 us""", size=8)
    R.H1("Appendix C: Normalised Merge Output")
    R.code("""B  Normalised merge (converted to UTC, clock offset removed)
  10:00:01.000000  + 0.000s  packet capture   suspicious inbound connection
  10:00:03.000000  + 2.000s  packet capture   repeated connection requests
  10:00:03.420000  + 2.420s  web server       POST /upload accepted
  10:00:05.000000  + 4.000s  packet capture   outbound transfer begins
  10:00:07.000000  + 6.000s  endpoint AV      script quarantined
  10:00:08.000000  + 7.000s  firewall         ALERT: unusual outbound volume
  10:00:12.000000  +11.000s  monitoring SIEM  correlated alert raised

C  Validate: every alert is later than first suspicious packet -> True""", size=8)
    R.H1("Appendix D: Reproduction Steps")
    R.numbered([
        "Install Python 3.10 or later, matplotlib, tcpdump and Wireshark’s command-line tools (tshark, capinfos, editcap).",
        "Run `python3 make_pcap.py` in the scripts folder to create the constructed captures in the data folder.",
        "Run `python3 parse_pcap.py ../data/handshake_us.pcap` and compare its output with `tcpdump -n -tttt -r` and `tshark -r ... -T fields -e frame.time_epoch`.",
        "Run `sudo ./live_capture.sh ../data/live_lo.pcap` to take a new live capture, then `python3 gap_analysis.py` on it. The times will differ from those in this report, but the two pauses will again appear as gaps close to 0.8 s and 1.5 s.",
        "Run `python3 timeline_merge.py`, `drift_model.py`, `tz_table.py` and `exfil_window.py` to reproduce Tables 4.3, 5.2, 5.3 and the exfiltration results.",
        "Run `python3 figures.py` to redraw every figure, and `python3 build_report.py` to regenerate the report."])
    R.P("The folder structure of the archive is:", after=3)
    R.code(readme_tree, size=8.5)
