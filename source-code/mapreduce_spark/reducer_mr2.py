#!/usr/bin/env python3
import sys

# Khởi tạo các biến kiểm soát trạng thái khóa (State Maintenance)
current_province = None
total_sum_precip = 0.0
total_sum_wind = 0.0
total_extreme = 0
total_count = 0

def output_result(province, sum_precip, sum_wind, extreme_count, count):
    """Hàm phụ trợ tính toán trung bình và in kết quả"""
    try:
        avg_precip = sum_precip / count
        avg_wind = sum_wind / count
        extreme_ratio = (extreme_count / count) * 100
        
        print(f"Tỉnh: {province}")
        print(f"   Lượng mưa TB           : {avg_precip:.2f} mm/ngày")
        print(f"   Tốc độ gió TB          : {avg_wind:.2f} km/h")
        print(f"   Số ngày thời tiết cực đoan : {extreme_count}/{count} ngày ({extreme_ratio:.1f}%)")
        print("-" * 65)
    except ZeroDivisionError:
        pass

for line in sys.stdin:
    line = line.strip()
    if not line: 
        continue
    
    try:
        province, values = line.split('\t')
        sum_precip_str, sum_wind_str, extreme_str, count_str = values.split('_')
        
        sum_precip = float(sum_precip_str)
        sum_wind = float(sum_wind_str)
        extreme = int(extreme_str)
        count = int(count_str)
        
        # Thuật toán gom nhóm toàn cục (Global Aggregation)
        if current_province == province:
            total_sum_precip += sum_precip
            total_sum_wind += sum_wind
            total_extreme += extreme
            total_count += count
        else:
            if current_province:
                output_result(current_province, total_sum_precip, total_sum_wind, total_extreme, total_count)
            
            # Reset trạng thái
            current_province = province
            total_sum_precip = sum_precip
            total_sum_wind = sum_wind
            total_extreme = extreme
            total_count = count
    except:
        pass

if current_province:
    output_result(current_province, total_sum_precip, total_sum_wind, total_extreme, total_count)
