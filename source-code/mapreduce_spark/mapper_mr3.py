#!/usr/bin/env python3
import sys
from datetime import datetime

local_cache = {}

for line in sys.stdin:
    line = line.strip()
    if not line or line.startswith('weather_date'): continue
    parts = line.split(',')
    if len(parts) < 4: continue
    
    try:
        date_str = parts[0].strip()
        region = parts[2].strip()
        temp = float(parts[3].strip())
        
        if temp < -5 or temp > 50: continue
        
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        month_key = f"{region}_{dt.strftime('%Y-%m')}"
        
        if month_key not in local_cache:
            local_cache[month_key] = {'sum':0.0, 'count':0}
        local_cache[month_key]['sum'] += temp
        local_cache[month_key]['count'] += 1
    except:
        pass

for key, data in local_cache.items():
    print(f"{key}\t{data['sum']}_{data['count']}")
