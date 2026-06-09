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
    province, humidity_str = parts
    try:
        humidity = float(humidity_str)
    except ValueError:
        continue
        
    if current_province == province:
        current_sum += humidity
        current_count += 1
    else:
        if current_province:
            avg_humidity = current_sum / current_count
            print(f"{current_province}\t{avg_humidity:.2f}")
        current_province = province
        current_sum = humidity
        current_count = 1

if current_province:
    avg_humidity = current_sum / current_count
    print(f"{current_province}\t{avg_humidity:.2f}")