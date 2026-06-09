#!/usr/bin/env python3
import sys

for line in sys.stdin:
    line = line.strip()
    if not line or line.startswith("weather_date"):
        continue
    parts = line.split(',')
    if len(parts) >= 4:
        date = parts[0]
        try:
            temperature = float(parts[3])
            print(f"max_temp\t{temperature},{date}")
        except ValueError:
            continue