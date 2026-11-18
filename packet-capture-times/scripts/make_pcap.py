#!/usr/bin/env python3
"""Build a classic libpcap file whose five frames carry the sample timestamps
used in the case study (TCP handshake + start of a TLS session).
Frames are real Ethernet/IPv4/TCP frames with valid checksums; only the
capture-record timestamps are chosen by us (this is a constructed capture)."""
import struct, sys
from ipaddress import IPv4Address

CLIENT, SERVER = "192.0.2.10", "198.51.100.7"     # RFC 5737 documentation range
MAC_C, MAC_S = bytes.fromhex("020000000001"), bytes.fromhex("020000000002")

def csum(b):
    if len(b) % 2: b += b"\0"
    s = sum(struct.unpack("!%dH" % (len(b)//2), b))
    while s >> 16: s = (s & 0xffff) + (s >> 16)
    return (~s) & 0xffff

def frame(src, dst, sport, dport, seq, ack, flags, payload=b"", ipid=0, win=64240, smac=MAC_C, dmac=MAC_S):
    opts = b""
    if flags & 0x02:  # SYN: MSS, SACK-permitted, TS, NOP, WScale  (20 bytes -> 74-byte frame)
        opts = bytes.fromhex("020405b4 0402080a 00000001 00000000 01030307".replace(" ", ""))
    else:             # established: NOP, NOP, TCP timestamp option (12 bytes)
        opts = bytes.fromhex("0101080a 00000002 00000001")
    off = (20 + len(opts)) // 4
    tcp0 = struct.pack("!HHIIBBHHH", sport, dport, seq, ack, off << 4, flags, win, 0, 0) + opts
    pseudo = IPv4Address(src).packed + IPv4Address(dst).packed + struct.pack("!BBH", 0, 6, len(tcp0)+len(payload))
    c = csum(pseudo + tcp0 + payload)
    tcp = tcp0[:16] + struct.pack("!H", c) + tcp0[18:] + payload
    ip0 = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20+len(tcp), ipid, 0x4000, 64, 6, 0,
                      IPv4Address(src).packed, IPv4Address(dst).packed)
    ip = ip0[:10] + struct.pack("!H", csum(ip0)) + ip0[12:]
    return dmac + smac + b"\x08\x00" + ip + tcp

# (seconds-since-epoch, microseconds, frame)  ; epoch 1794246001 = 2026-11-09 17:40:01 UTC
T = 1794246001
ch = b"\x16\x03\x01\x02\x00\x01\x00\x01\xfc\x03\x03" + (bytes(range(256))*2)[:505-11]   # 571-byte frame (505-byte payload)
sh = b"\x16\x03\x03\x04\x00\x02\x00\x00\x76\x03\x03" + (bytes(range(256))*6)[:1448-11]  # 1514-byte frame (1448-byte payload)
frames = [
 (T, 212754, frame(CLIENT, SERVER, 51522, 443, 1043210, 0,       0x02, ipid=1)),
 (T, 213981, frame(SERVER, CLIENT, 443, 51522, 7712009, 1043211, 0x12, win=65535, smac=MAC_S, dmac=MAC_C)),
 (T, 214020, frame(CLIENT, SERVER, 51522, 443, 1043211, 7712010, 0x10, win=502, ipid=2)),
 (T, 247566, frame(CLIENT, SERVER, 51522, 443, 1043211, 7712010, 0x18, payload=ch, win=502, ipid=3)),
 (T, 276694, frame(SERVER, CLIENT, 443, 51522, 7712010, 1043711, 0x18, payload=sh, win=65535, smac=MAC_S, dmac=MAC_C)),
]

def write(path, nano=False):
    magic = 0xa1b23c4d if nano else 0xa1b2c3d4
    with open(path, "wb") as f:
        f.write(struct.pack("<IHHiIII", magic, 2, 4, 0, 0, 65535, 1))   # 24-byte global header, LINKTYPE_ETHERNET
        for s, us, fr in frames:
            frac = us * 1000 if nano else us
            f.write(struct.pack("<IIII", s, frac, len(fr), len(fr)))     # 16-byte record header
            f.write(fr)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "../data/handshake_us.pcap"
    write(out); write(out.replace("_us", "_ns"), nano=True)
    print("frame lengths:", [len(f[2]) for f in frames])
