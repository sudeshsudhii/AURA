#!/usr/bin/env python3
"""SYNTHETIC demonstration (not Target data, not a real capture).
Generates outbound-FTP session records that follow the documented pattern from the Senate report
(about 11 GB over about two weeks, transfers between 10:00 and 18:00 US Central time, 2-15 Dec 2013),
then shows how an analyst finds the window - and how the answer looks in UTC vs local time.
The window matches the documented pattern BY CONSTRUCTION; the point is the method."""
import random, json, sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
random.seed(2013)
CT = ZoneInfo("America/Chicago")
sessions = []
for day in range(14):
    d = datetime(2013,12,2,tzinfo=CT) + timedelta(days=day)
    for _ in range(random.randint(10, 14)):
        start = d.replace(hour=10) + timedelta(seconds=random.randint(0, 8*3600 - 600))
        dur = random.randint(60, 540)
        mb = random.uniform(40, 120) * dur / 300
        sessions.append((start.astimezone(timezone.utc), dur, mb))
# a few benign business-hours FTP sessions from other hosts would normally be mixed in; omitted for clarity
total_gb = sum(s[2] for s in sessions) / 1024
scale = 11.0 / total_gb                       # scale volumes so the total is the reported ~11 GB
sessions = [(t, d, mb*scale) for t, d, mb in sessions]
def hist(zone):
    h = [0.0]*24
    for t, d, mb in sessions: h[t.astimezone(zone).hour] += mb/1024
    return h
hu, hc = hist(timezone.utc), hist(CT)
print(f"sessions: {len(sessions)}  total volume: {sum(s[2] for s in sessions)/1024:.2f} GB  first: {min(s[0] for s in sessions):%Y-%m-%d %H:%M} UTC  last: {max(s[0] for s in sessions):%Y-%m-%d %H:%M} UTC")
def window(h):
    act = [i for i, v in enumerate(h) if v > 0.01*sum(h)]
    return min(act), max(act)+1
print("active hours, UTC view    : %02d:00-%02d:00" % window(hu))
print("active hours, Central view: %02d:00-%02d:00 (CST = UTC-6 in December)" % window(hc))
print("share of volume 10:00-18:00 Central: %.1f%%" % (100*sum(hc[10:18])/sum(hc)))
print("share of volume 00:00-06:00 UTC (a 'night' for a UTC-reading analyst): %.1f%%, 16:00-24:00 UTC: %.1f%%" % (100*sum(hu[0:6])/sum(hu), 100*sum(hu[16:24])/sum(hu)))
json.dump({"utc": hu, "central": hc, "n": len(sessions), "gb": sum(s[2] for s in sessions)/1024}, open("../data/exfil_hist.json","w"))
