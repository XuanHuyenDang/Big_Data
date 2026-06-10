#!/usr/bin/env python3
import sys

current_key = None
total_sum = 0.0
total_count = 0

for line in sys.stdin:
    try:
        key, values = line.strip().split('\t')
        sum_val, count = map(float, values.split('_'))
        count = int(count)
        
        if current_key == key:
            total_sum += sum_val
            total_count += count
        else:
            if current_key:
                region, month = current_key.split('_')
                avg_temp = total_sum / total_count
                print(f"{region} | {month} | Nhiệt độ TB: {avg_temp:.2f} °C")
            
            current_key = key
            total_sum = sum_val
            total_count = count
    except:
        pass

# Dòng cuối cùng
if current_key:
    region, month = current_key.split('_')
    avg_temp = total_sum / total_count
    print(f"{region} | {month} | Nhiệt độ TB: {avg_temp:.2f} °C")
