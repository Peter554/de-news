#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# ///

from datetime import date, timedelta
from pathlib import Path

start_date = date(2025, 9, 17)
end_date = date.today()

missing_dates: list[str] = []
d = start_date
while d <= end_date:
    date_str = d.isoformat()
    if not Path("data", "articles", date_str).exists():
        missing_dates.append(date_str)
    d += timedelta(days=1)

if not missing_dates:
    print("No missing dates found!")
else:
    print(f"Found {len(missing_dates)} missing date(s):\n")
    for date_str in missing_dates:
        print(date_str)
