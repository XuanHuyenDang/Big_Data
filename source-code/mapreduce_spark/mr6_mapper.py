#!/usr/bin/env python3
import sys

for line in sys.stdin:
    line = line.strip()
    if not line or line.startswith("weather_date"):
        continue
    parts = line.split(',')
    if len(parts) >= 7:
        province = parts[1]
        try:
            wind_speed = float(parts[6])
            print(f"{province}\t{wind_speed}")
        except ValueError:
            continue