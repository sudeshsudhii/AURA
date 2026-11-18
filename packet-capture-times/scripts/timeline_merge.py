#!/usr/bin/env python3
"""Normalise and merge events from sources with different zones, offsets and precision.
Implements the 5 steps: record -> convert -> correct -> merge -> validate.
HYPOTHETICAL data (invented times) - demonstrates the method only."""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

# step 1: RECORD  (metadata for every source)
SOURCES = {
  "packet capture":  dict(tz="UTC",              offset=0.0,   res=1e-6, note="NTP-synced sensor"),
  "firewall":        dict(tz="Asia/Kolkata",     offset=+4.0,  res=1.0,  note="log clock measured 4 s fast"),
  "web server":      dict(tz="UTC",              offset=0.0,   res=1e-3, note="NTP-synced"),
  "endpoint AV":     dict(tz="America/New_York", offset=-2.0,  res=1.0,  note="log clock measured 2 s slow"),
  "monitoring SIEM": dict(tz="UTC",              offset=0.0,   res=1.0,  note="NTP-synced"),
}
# raw log lines as written by each system (local wall-clock strings)
RAW = [
 ("packet capture",  "2026-11-09 10:00:01.000000", "suspicious inbound connection"),
 ("packet capture",  "2026-11-09 10:00:03.000000", "repeated connection requests"),
 ("web server",      "2026-11-09 10:00:03.420",    "POST /upload accepted"),
 ("packet capture",  "2026-11-09 10:00:05.000000", "outbound transfer begins"),
 ("endpoint AV",     "2026-11-09 05:00:05",        "script quarantined"),          # NY local, clock 2 s slow
 ("firewall",        "2026-11-09 15:30:12",        "ALERT: unusual outbound volume"),  # IST local, clock 4 s fast
 ("monitoring SIEM", "2026-11-09 10:00:12",        "correlated alert raised"),
]
def parse_local(s, tz):
    fmt = "%Y-%m-%d %H:%M:%S.%f" if "." in s else "%Y-%m-%d %H:%M:%S"
    return datetime.strptime(s, fmt).replace(tzinfo=ZoneInfo(tz))

def run():
    naive, fixed = [], []
    for src, raw, msg in RAW:
        m = SOURCES[src]
        local = parse_local(raw, m["tz"])
        naive.append((datetime.strptime(raw, "%Y-%m-%d %H:%M:%S.%f" if "." in raw else "%Y-%m-%d %H:%M:%S"), src, msg))  # step "none": sort raw strings
        utc = local.astimezone(timezone.utc)                         # step 2: CONVERT
        corr = utc - timedelta(seconds=m["offset"])                  # step 3: CORRECT
        fixed.append((corr, src, msg, raw, m["res"]))
    naive.sort(key=lambda x: x[0])
    fixed.sort(key=lambda x: x[0])                                   # step 4: MERGE
    return naive, fixed

if __name__ == "__main__":
    naive, fixed = run()
    print("A. Naive merge (raw local strings sorted as if all were the same zone)")
    for t, s, m in naive: print(f"  {t:%H:%M:%S.%f}  {s:<16} {m}")
    print("\nB. Normalised merge (converted to UTC, clock offset removed)")
    t0 = fixed[0][0]
    for t, s, m, raw, res in fixed:
        print(f"  {t:%H:%M:%S.%f}  +{(t-t0).total_seconds():>6.3f}s  {s:<16} {m}   [raw: {raw}, res {res:g}s]")
    # step 5: VALIDATE - alerts must not precede the activity they report
    act = [t for t, s, *_ in fixed if s == "packet capture"]
    alerts = [(t, s) for t, s, *_ in fixed if s in ("firewall", "monitoring SIEM")]
    ok = all(a >= min(act) for a, _ in alerts) and (max(a for a,_ in alerts) - min(act)).total_seconds() > 0
    print("\nC. Validate: every alert is later than first suspicious packet ->", ok)
    first_alert = min(a for a, _ in alerts)
    print(f"   packets show activity from 10:00:01; first alert {(first_alert-min(act)).total_seconds():.0f} s later, last alert {(max(a for a,_ in alerts)-min(act)).total_seconds():.0f} s later")
