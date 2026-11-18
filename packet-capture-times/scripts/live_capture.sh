#!/usr/bin/env bash
# Live capture on the loopback interface: one TCP echo exchange with human-like pauses.
# Needs root (or CAP_NET_RAW) for tcpdump.  Usage: live_capture.sh <out.pcap>
OUT=${1:-../data/live_lo.pcap}
tcpdump -n -i lo -w "$OUT" --time-stamp-precision=micro 'tcp port 9099' 2>/dev/null &
TP=$!; sleep 1.5
python3 - <<'PY' &
import socket
s=socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1); s.bind(("127.0.0.1",9099)); s.listen(1)
c,_=s.accept()
while True:
    d=c.recv(100)
    if not d: break
    c.sendall(d)
PY
SP=$!; sleep 0.5
python3 - <<'PY'
import socket, time
c=socket.create_connection(("127.0.0.1",9099))
for msg, pause in ((b"hello", 0.8), (b"whoami", 1.5), (b"cat /etc/passwd", 0)):
c.close()
PY
sleep 1; kill $TP 2>/dev/null; wait $TP 2>/dev/null; kill $SP 2>/dev/null
