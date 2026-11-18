# Packet Capture Times - case study report

* `Packet_Capture_Times_Case_Study_Report.docx` - the report (SRMIST case-study template format). A PDF copy is alongside it.
* `scripts/` - everything needed to regenerate the experiments, figures and the report (see Appendix D of the report).
* `data/` - constructed capture (`handshake_*.pcap*`), live loopback capture (`live_lo.pcap`), synthetic exfil data.
* `output/` - saved tool output quoted in the report.
* `figures/` - the 13 figures.

Check layout: `python3 scripts/layout_audit.py <report.docx> <report.pdf>` (margins, centring, page numbers, stretched lines, alignment).

Regenerate: `cd scripts && python3 make_pcap.py && sudo ./live_capture.sh ../data/live_lo.pcap && python3 figures.py && python3 build_report.py <template.docx> ../output/Report.docx`

Data kinds are labelled throughout the report: constructed, live, synthetic, hypothetical, reported.
