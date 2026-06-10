#!/usr/bin/env python3
import sys

global_max_score = -float('inf')
best_province = ""
best_region = ""
best_date = ""
best_temp = 0.0
best_precip = 0.0
best_wind = 0.0

for line in sys.stdin:
    try:
        parts = line.strip().split('\t')
        if len(parts) != 8: continue
        
        key = parts[0] # Key luôn là GLOBAL_MAX
        score = float(parts[1])
        province = parts[2]
        region = parts[3]
        temp = float(parts[4])
        precip = float(parts[5])
        wind = float(parts[6])
        date = parts[7]

        if score > global_max_score:
            global_max_score = score
            best_province = province
            best_region = region
            best_date = date
            best_temp = temp
            best_precip = precip
            best_wind = wind
    except:
        pass

if best_province:
    print("NGÀY THỜI TIẾT KHẮC NGHIỆT NHẤT VIỆT NAM 2025")
    print(f"Tỉnh: {best_province} ({best_region})")
    print(f"Ngày: {best_date}")
    print(f"Nhiệt độ     : {best_temp:.1f} °C")
    print(f"Lượng mưa    : {best_precip:.1f} mm")
    print(f"Tốc độ gió   : {best_wind:.1f} km/h")
    print(f"Extreme Score: {global_max_score:.1f}")
