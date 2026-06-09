#!/usr/bin/env python3
import sys

current_province = None
current_sum = 0
current_count = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    parts = line.split('\t')
    if len(parts) != 2:
        continue
    province, wind_speed_str = parts
    try:
        wind_speed = float(wind_speed_str)
    except ValueError:
        continue
        
    if current_province == province:
        current_sum += wind_speed
        current_count += 1
    else:
        if current_province:
            avg_wind = current_sum / current_count
            print(f"{current_province}\t{avg_wind:.2f}")
        current_province = province
        current_sum = wind_speed
        current_count = 1

if current_province:
    avg_wind = current_sum / current_count
    print(f"{current_province}\t{avg_wind:.2f}")