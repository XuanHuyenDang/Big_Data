import requests
import pandas as pd
from datetime import datetime
import calendar
import time

#Cấu hình Trạm và API Key
stations = {
    'Ho_Chi_Minh': 'VVTS',
    'Can_Tho': 'VVCT',
    'Ca_Mau': 'VVCM'
}
API_KEY = "e1f10a1e78da46f5b10a1e78da96f525" 

#Sinh danh sách 12 tháng lùi về trước
date_chunks = []
today = datetime.now()

for i in range(12):
    m = today.month - i
    y = today.year
    if m <= 0:
        m += 12
        y -= 1
    last_day = calendar.monthrange(y, m)[1]
    start_str = f"{y:04d}{m:02d}01"
    end_str = f"{y:04d}{m:02d}{last_day}"
    date_chunks.append((start_str, end_str, f"{m:02d}/{y}"))

all_data = []

#Danh sách toàn bộ các cột có thể có từ JSON của Wunderground
all_possible_columns = [
    'valid_time_gmt', 'temp', 'dewPt', 'rh', 'wdir_cardinal', 
    'wspd', 'wgust', 'pressure', 'precip_total', 'uv_index', 'vis', 'wx_phrase'
]

#Vòng lặp lấy dữ liệu
for city, code in stations.items():
    print(f"\nĐang xử lý trạm: {city}")
    
    for start_date, end_date, month_label in date_chunks:
        print(f"Lấy tháng {month_label}...", end=" ")
        
        url = f"https://api.weather.com/v1/location/{code}:9:VN/observations/historical.json?apiKey={API_KEY}&units=m&startDate={start_date}&endDate={end_date}"
        
        try:
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                records = response.json().get('observations', [])
                
                if records:
                    df = pd.DataFrame(records)
                    
                    # Đảm bảo DataFrame có đủ tất cả các cột, nếu thiếu thì điền NaN
                    for col in all_possible_columns:
                        if col not in df.columns:
                            df[col] = pd.NA
                    
                    #TIỀN XỬ LÝ THỜI GIAN
                    df['Local_Time'] = pd.to_datetime(df['valid_time_gmt'], unit='s') + pd.Timedelta(hours=7)
                    df['Date'] = df['Local_Time'].dt.strftime('%Y-%m-%d')
                    
                    #TÌM NHIỆT ĐỘ MIN/MAX CẢ NGÀY
                    daily_min_max = df.groupby('Date')['temp'].agg(Min_Temp_C='min', Max_Temp_C='max').reset_index()
                    # LỌC LẤY DÒNG GẦN 12H TRƯA NHẤT
                    # Khung giờ từ 10:00 sáng đến 14:59 chiều
                    df_noon = df[(df['Local_Time'].dt.hour >= 10) & (df['Local_Time'].dt.hour <= 14)].copy()
                    
                    # Tính khoảng cách phút từ giờ ghi nhận đến đúng 12:00
                    df_noon['diff_to_12'] = abs((df_noon['Local_Time'].dt.hour * 60 + df_noon['Local_Time'].dt.minute) - (12 * 60))
                    
                    # Ưu tiên dòng gần 12h nhất, nếu trùng thì lấy dòng cập nhật sau cùng
                    df_noon = df_noon.sort_values(['Date', 'diff_to_12', 'Local_Time'])
                    
                    #Giữ lại đúng 1 dòng đại diện cho mỗi ngày
                    df_12h = df_noon.drop_duplicates(subset=['Date'], keep='first').copy()
                    
                    # GHÉP NỐI & LÀM SẠCH BẢNG
                    df_merged = pd.merge(df_12h, daily_min_max, on='Date', how='left')
                    df_merged['Province'] = city
                    
                    # Chuyển đổi Local_Time sang string dạng Giờ:Phút để biết chính xác mốc lấy dữ liệu
                    df_merged['Time_Recorded'] = df_merged['Local_Time'].dt.strftime('%H:%M')
                    
                    # Lựa chọn và sắp xếp các cột chuẩn
                    ordered_columns = [
                        'Province', 'Date', 'Time_Recorded', 'Min_Temp_C', 'Max_Temp_C',
                        'temp', 'dewPt', 'rh', 'wx_phrase', 'wdir_cardinal', 
                        'wspd', 'wgust', 'pressure', 'precip_total', 'uv_index', 'vis'
                    ]
                    df_clean = df_merged[ordered_columns].copy()
                    
                    # Đổi tên cột
                    df_clean.columns = [
                        'Province', 'Date', 'Time_Recorded_12h', 
                        'Min_Temp_C_Day', 'Max_Temp_C_Day', 'Temp_C_12h', 
                        'DewPoint_C_12h', 'Humidity_%_12h', 'Condition_12h', 
                        'WindDirection_12h', 'WindSpeed_kmh_12h', 'WindGust_kmh_12h', 
                        'Pressure_mb_12h', 'Precipitation_mm_12h', 'UV_Index_12h', 'Visibility_km_12h'
                    ]
                    
                    all_data.append(df_clean)
                    print(f"[OK] - Lấy được {len(df_clean)} ngày.")
                else:
                    print("[!] Không có dữ liệu.")
            else:
                print(f"[x] Lỗi API: {response.status_code}")
                
        except Exception as e:
            print(f"[x] Lỗi mạng hoặc kết nối.")
            
        time.sleep(1.5) # Nghỉ 1.5 giây giữa các lần gọi API để tránh bị chặn

#Gom dữ liệu và Xuất file
if all_data:
    final_df = pd.concat(all_data, ignore_index=True)
    
    # Sắp xếp tổng thể theo Tỉnh và Ngày tăng dần
    final_df = final_df.sort_values(by=['Province', 'Date']).reset_index(drop=True)
    
    file_name = 'Wunderground_12Months_AllAttributes.csv'
    final_df.to_csv(file_name, index=False, encoding='utf-8-sig')
    
    print("\n" + "="*70)
    print(f"Hoàn tất! Dataset siêu lớn với {len(final_df)} dòng và 16 cột.")
    print(f"File lưu tại: '{file_name}'")
    
    # Hiển thị tóm tắt bộ dữ liệu
    print("\nThông tin bộ dữ liệu (5 dòng đầu, 7 cột đầu):")
    print(final_df.iloc[:, :7].head())