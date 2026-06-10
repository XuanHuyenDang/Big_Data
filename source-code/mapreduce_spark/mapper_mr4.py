#!/usr/bin/env python3
import sys

# Khởi tạo các biến để lưu kỷ lục cục bộ
max_score = -float('inf')
best_record = None

for line in sys.stdin:
    line = line.strip()
    if not line or line.startswith('weather_date'): continue
    parts = line.split(',')
    if len(parts) < 7: continue
    
    try:
        date = parts[0].strip()
        province = parts[1].strip()
        region = parts[2].strip()
        temp = float(parts[3].strip())
        precip = float(parts[5].strip())
        wind = float(parts[6].strip())
        
        # Lọc dữ liệu lỗi/ngoại lai
        if temp < -5 or temp > 50 or precip < 0 or wind < 0: continue
        
        # Tính điểm khắc nghiệt
        extreme_score = temp + precip * 2 + wind * 1.5
        
        # Nếu tìm thấy điểm cao hơn, cập nhật lại kỷ lục cục bộ
        if extreme_score > max_score:
            max_score = extreme_score
            best_record = f"GLOBAL_MAX\t{max_score}\t{province}\t{region}\t{temp}\t{precip}\t{wind}\t{date}"
    except:
        pass
if best_record:
    print(best_record)
