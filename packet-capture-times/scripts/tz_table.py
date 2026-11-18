#!/usr/bin/env python3
"""One instant (14:30:00 UTC, 9 Nov 2026) shown in five zones, from the IANA tz database."""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
t = datetime(2026,11,9,14,30,0,tzinfo=timezone.utc)
print(f"{'zone':<20}{'abbr':<6}{'offset':<8}local reading")
for name in ("UTC","Europe/London","America/New_York","Asia/Kolkata","Asia/Tokyo","Australia/Sydney"):
    l = t.astimezone(ZoneInfo(name)); off = l.utcoffset().total_seconds()/3600
    print(f"{name:<20}{l.tzname():<6}{off:+.1f}h  {l:%H:%M:%S, %d %b}")
print("epoch of the instant:", int(t.timestamp()))
print("epoch 1e9 ->", datetime.fromtimestamp(10**9, timezone.utc), "| epoch 0 ->", datetime.fromtimestamp(0, timezone.utc))
print("sample 1794246001 ->", datetime.fromtimestamp(1794246001, timezone.utc))
