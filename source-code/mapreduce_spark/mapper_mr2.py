#!/usr/bin/env python3
import sys

# Khởi tạo bộ nhớ đệm cục bộ (In-Mapper Combining)
local_cache = {}

for line in sys.stdin:
    line = line.strip()
    if not line or line.startswith('weather_date'): 
        continue
    
    parts = line.split(',')
    if len(parts) < 7: 
        continue
    
    try:
        province = parts[1].strip()
        precip = float(parts[5].strip())
        wind = float(parts[6].strip())
        
        if precip < 0 or wind < 0: 
            continue
        
        is_extreme = 1 if (precip >= 30 or wind >= 25) else 0
        
        # Gom nhóm cục bộ 
        if province not in local_cache:
            local_cache[province] = {'sum_precip': 0.0, 'sum_wind': 0.0, 'extreme': 0, 'count': 0}
        
        local_cache[province]['sum_precip'] += precip
        local_cache[province]['sum_wind'] += wind
        local_cache[province]['extreme'] += is_extreme
        local_cache[province]['count'] += 1
    except:
        pass

# Xuất dữ liệu trung gian
for prov, data in local_cache.items():
    print(f"{prov}\t{data['sum_precip']}_{data['sum_wind']}_{data['extreme']}_{data['count']}")
