#!/usr/bin/env python3
import sys

# Khởi tạo bộ nhớ đệm cục bộ cho Mapper
local_cache = {}

for line in sys.stdin:
    line = line.strip()
    if not line or line.startswith('weather_date'): 
        continue
    parts = line.split(',')
    if len(parts) < 5: 
        continue
    
    try:
        province = parts[1].strip()
        region = parts[2].strip()
        temp = float(parts[3].strip())
        humidity = float(parts[4].strip())
        
        # Bộ lọc loại bỏ dữ liệu dị thường
        if temp < -5 or temp > 50 or humidity < 10 or humidity > 100: 
            continue
        
        key = f"{province}|{region}"
        
        if key not in local_cache:
            local_cache[key] = {'sum_temp': 0.0, 'sum_hum': 0.0, 'count': 0}
        
        local_cache[key]['sum_temp'] += temp
        local_cache[key]['sum_hum'] += humidity
        local_cache[key]['count'] += 1
    except:
        pass

# Xuất dữ liệu trung gian sau khi đã gộp cục bộ
for key, data in local_cache.items():
    print(f"{key}\t{data['sum_temp']}_{data['sum_hum']}_{data['count']}")
