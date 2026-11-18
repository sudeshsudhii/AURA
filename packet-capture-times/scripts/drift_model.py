#!/usr/bin/env python3
"""Clock-drift arithmetic and the firewall/server example (HYPOTHETICAL times)."""
print("A. Drift of a clock running fast by P parts-per-million")
print(f"{'ppm':>5} {'per day (s)':>12} {'per 30 d (s)':>13} {'per year (s)':>13} {'days to 10 min':>15}")
for ppm in (5, 20, 50, 100):
    d = ppm*1e-6*86400
    print(f"{ppm:>5} {d:>12.3f} {d*30:>13.2f} {d*365:>13.1f} {600/d:>15.0f}")
print("\nB. Firewall (clock 4 min 10 s fast) vs NTP-synced server")
from datetime import datetime, timedelta
fw_true = datetime(2026,11,9,14,29,58); srv = datetime(2026,11,9,14,30,0)
off = timedelta(minutes=4, seconds=10)
fw_logged = fw_true + off
print("   firewall logged :", fw_logged.time(), " server logged:", srv.time())
print("   raw order       :", "SERVER login first" if srv < fw_logged else "firewall first", "-> login appears", f"{(fw_logged-srv).seconds//60} min {(fw_logged-srv).seconds%60} s BEFORE the allow (impossible)")
print("   corrected order :", (fw_logged-off).time(), "firewall allow ->", srv.time(), "login (cause precedes effect)")
