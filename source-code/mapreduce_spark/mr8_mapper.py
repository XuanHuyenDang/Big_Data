#!/usr/bin/env python3
import sys

for line in sys.stdin:
    line = line.strip()
    if not line or line.startswith("weather_date"):
        continue
    parts = line.split(',')
    if len(parts) >= 6:
        date = parts[0]
        try:
            precipitation = float(parts[5])
            print(f"max_precip\t{precipitation},{date}")
        except ValueError:
            continue