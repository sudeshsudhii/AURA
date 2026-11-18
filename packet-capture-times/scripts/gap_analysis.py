#!/usr/bin/env python3
"""Inter-packet gap analysis of a capture (uses parse_pcap.py): machine-speed vs human-speed gaps."""
import sys; sys.path.insert(0, __file__.rsplit("/",1)[0])
from parse_pcap import parse
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    unit, rows = parse(sys.argv[1])
gaps = [(r[0], float(r[8])) for r in rows[1:]]
print(f"{len(rows)} frames, duration {float(rows[-1][7]):.6f} s")
print("gap bands:  <1 ms = machine, 1-100 ms = network/stack, >=0.5 s = pause (human/think time)")
bands = {"< 1 ms":0, "1 ms - 100 ms":0, "100 ms - 0.5 s":0, ">= 0.5 s":0}
for _, g in gaps:
    k = "< 1 ms" if g < 1e-3 else "1 ms - 100 ms" if g < .1 else "100 ms - 0.5 s" if g < .5 else ">= 0.5 s"
    bands[k] += 1
for k, v in bands.items(): print(f"  {k:<16}{v:>3}")
print("largest gaps:", ", ".join(f"frame {n}: {g:.6f} s" for n, g in sorted(gaps, key=lambda x: -x[1])[:3]))
print(f"SYN -> SYN/ACK : {gaps[0][1]*1e6:.0f} us")
