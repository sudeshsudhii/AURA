#!/usr/bin/env python3
"""Decode a classic pcap file by hand: global header, per-record header, timestamp arithmetic."""
import struct, sys, datetime
from decimal import Decimal

def parse(path):
    d = open(path, "rb").read()
    magic = struct.unpack("<I", d[:4])[0]
    unit = {0xa1b2c3d4: ("microsecond", 6), 0xa1b23c4d: ("nanosecond", 9)}[magic]
    ver_maj, ver_min, tz, sig, snap, link = struct.unpack("<HHiIII", d[4:24])
    print(f"magic=0x{magic:08x} ({unit[0]} stamps) version={ver_maj}.{ver_min} snaplen={snap} linktype={link}")
    off, n, prev, first = 24, 0, None, None
    rows = []
    while off < len(d):
        ts_sec, ts_frac, incl, orig = struct.unpack("<IIII", d[off:off+16]); off += 16
        t = Decimal(ts_sec) + Decimal(ts_frac) / Decimal(10**unit[1])
        n += 1; first = first if first is not None else t
        utc = datetime.datetime.fromtimestamp(ts_sec, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        rows.append((n, ts_sec, ts_frac, t, utc, incl, orig, t-first, (t-prev) if prev is not None else Decimal(0)))
        prev = t; off += incl
    return unit, rows

if __name__ == "__main__":
    unit, rows = parse(sys.argv[1])
    print(f"{'#':>2} {'ts_sec':>10} {'ts_frac':>9} {'epoch (s)':>18} {'UTC':>19} {'incl':>5} {'orig':>5} {'since 1st':>10} {'delta':>9}")
    for n, s, f, t, utc, i, o, rel, dl in rows:
        print(f"{n:>2} {s:>10} {f:>9} {t:>18.6f} {utc:>19} {i:>5} {o:>5} {rel:>10} {dl:>9}")
