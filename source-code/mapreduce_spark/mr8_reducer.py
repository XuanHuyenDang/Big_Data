#!/usr/bin/env python3
import sys

max_precip = -1.0
wettest_date = None

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    parts = line.split('\t')
    if len(parts) != 2:
        continue
    key, val = parts
    try:
        precip_str, date = val.split(',')
        precip = float(precip_str)
        if precip > max_precip:
            max_precip = precip
            wettest_date = date
    except ValueError:
        continue

if wettest_date:
    print(f"Highest_Precipitation_Day:\t{wettest_date}\tPrecipitation:\t{max_precip:.2f}")