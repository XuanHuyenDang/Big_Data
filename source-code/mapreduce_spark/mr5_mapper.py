#!/usr/bin/env python3
import sys

for line in sys.stdin:
    line = line.strip()
    if not line or line.startswith("weather_date"):
        continue
    parts = line.split(',')
    if len(parts) >= 5:
        province = parts[1]
        try:
            humidity = float(parts[4])
            print(f"{province}\t{humidity}")
        except ValueError:
            continue