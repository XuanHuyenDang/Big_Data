#!/usr/bin/env python3
import sys

# Khởi tạo các biến kiểm soát trạng thái khóa (State Maintenance)
current_key = None
total_sum_temp = 0.0
total_sum_hum = 0.0
total_count = 0

def output_result(key, sum_temp, sum_hum, count):
    #Hàm phụ trợ tính toán trung bình và in kết quả chuẩn
    try:
        avg_temp = sum_temp / count
        avg_hum = sum_hum / count
        province, region = key.split('|')
        
        discomfort_index = avg_temp + 0.555 * (0.1 * avg_hum * (avg_temp - 14.5) if avg_temp > 14.5 else 0)
        
        print(f"{province} ({region})\tNhiệt độ TB: {avg_temp:.2f}°C\tĐộ ẩm TB: {avg_hum:.1f}%\tDiscomfort Index: {discomfort_index:.1f}")
    except:
        pass

for line in sys.stdin:
    line = line.strip()
    if not line: 
        continue
        
    try:
        key, values = line.split('\t')
        sum_temp_str, sum_hum_str, count_str = values.split('_')
        
        sum_temp = float(sum_temp_str)
        sum_hum = float(sum_hum_str)
        count = int(count_str)
        
        # Nếu khóa trùng với khóa đang xử lý -> Tiến hành cộng dồn tích lũy
        if current_key == key:
            total_sum_temp += sum_temp
            total_sum_hum += sum_hum
            total_count += count
        else:
            # Nếu gặp khóa mới và đã có dữ liệu tích lũy trước đó -> Xuất kết quả cụm cũ
            if current_key:
                output_result(current_key, total_sum_temp, total_sum_hum, total_count)
            
            # Reset trạng thái để chuẩn bị tích lũy cho cụm khóa mới
            current_key = key
            total_sum_temp = sum_temp
            total_sum_hum = sum_hum
            total_count = count
    except:
        pass

if current_key:
    output_result(current_key, total_sum_temp, total_sum_hum, total_count)
