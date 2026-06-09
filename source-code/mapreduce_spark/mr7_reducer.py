#!/usr/bin/env python3
import sys

max_temp = -999.0
hottest_date = None

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    parts = line.split('\t')
    if len(parts) != 2:
        continue
    key, val = parts
    try:
        temp_str, date = val.split(',')
        temp = float(temp_str)
        if temp > max_temp:
            max_temp = temp
            hottest_date = date
    except ValueError:
        continue

if hottest_date:
    print(f"Hottest_Day:\t{hottest_date}\tMax_Temperature:\t{max_temp:.2f}")