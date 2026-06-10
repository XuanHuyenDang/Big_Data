import requests
import pandas as pd
import calendar
import time
import os

# Cấu hình Trạm và API Key với 4 trạm độc lập
stations = {
    'TP.HCM': 'VVTS',
    'Cà Mau': 'VVCM',
    'Phú Quốc': 'VVPQ',
    'Côn Đảo': 'VVCS'
}
API_KEY = os.getenv("WEATHER_API_KEY", "e1f10a1e78da46f5b10a1e78da96f525")
region = "South"

# Sinh danh sách 12 tháng của năm 2025
date_chunks = []
target_year = 2025

for m in range(1, 13):
    last_day = calendar.monthrange(target_year, m)[1]
    start_str = f"{target_year}{m:02d}01"
    end_str = f"{target_year}{m:02d}{last_day}"
    date_chunks.append((start_str, end_str, f"{m:02d}/{target_year}"))

all_data = []

# Codemap theo Weather Company icon codes (Giai đoạn 1: Trả về số)
def map_weather_code(row):
    phrase = str(row.get('wx_phrase', '')).lower()
    icon = row.get('wx_icon')

    if pd.notna(icon):
        try:
            icon = int(icon)
        except:
            icon = None
    else:
        icon = None

    icon_map = {
        0: 200,   # Tornado
        4: 200,   # Thunderstorms
        5: 610,   # Rain / Snow
        6: 611,   # Rain / Sleet
        7: 613,   # Wintry Mix
        8: 300,   # Freezing Drizzle
        9: 300,   # Drizzle
        10: 511,  # Freezing Rain
        11: 521,  # Showers
        12: 500,  # Rain
        13: 620,  # Flurries
        14: 621,  # Snow Showers
        15: 621,  # Blowing / Drifting Snow
        16: 600,  # Snow
        17: 906,  # Hail
        18: 611,  # Sleet
        19: 751,  # Dust / Sandstorm
        20: 741,  # Foggy
        21: 721,  # Haze
        22: 711,  # Smoke
        24: 781,  # Windy
        25: 511,  # Frigid / Ice Crystals
        26: 804,  # Cloudy
        27: 803,  # Mostly Cloudy Night
        28: 803,  # Mostly Cloudy Day
        29: 802,  # Partly Cloudy Night
        30: 802,  # Partly Cloudy Day
        31: 800,  # Clear Night
        32: 800,  # Sunny Day
        33: 801,  # Fair / Mostly Clear Night
        34: 801,  # Fair / Mostly Sunny Day
        35: 906,  # Mixed Rain and Hail
        36: 800,  # Hot
        37: 200,  # Isolated Thunderstorms
        38: 200,  # Scattered Thunderstorms
        39: 521,  # Scattered Showers
        40: 520,  # Heavy Rain
        41: 621,  # Scattered Snow Showers
        42: 622,  # Heavy Snow
        43: 602,  # Blizzard
        44: 999,  # Not Available
        45: 521,  # Scattered Showers
        46: 621,  # Scattered Snow Showers
        47: 200,  # Scattered Thunderstorms
    }

    if icon in icon_map:
        return icon_map[icon]

    if 'thunder' in phrase or 'storm' in phrase:
        return 200
    if 'drizzle' in phrase:
        return 300
    if 'freezing rain' in phrase:
        return 511
    if 'rain' in phrase or 'shower' in phrase:
        return 500
    if 'snow' in phrase:
        return 600
    if 'sleet' in phrase:
        return 611
    if 'hail' in phrase:
        return 906
    if 'fog' in phrase:
        return 741
    if 'haze' in phrase:
        return 721
    if 'smoke' in phrase:
        return 711
    if 'wind' in phrase:
        return 781
    if 'cloud' in phrase or 'overcast' in phrase:
        return 804
    if 'clear' in phrase or 'sunny' in phrase:
        return 800

    return 999

# Vòng lặp lấy dữ liệu
for province, code in stations.items():
    print(f"\nĐang xử lý trạm: {province} ({code})")

    for start_date, end_date, month_label in date_chunks:
        print(f"Lấy tháng {month_label}...", end=" ")

        url = f"https://api.weather.com/v1/location/{code}:9:VN/observations/historical.json?apiKey={API_KEY}&units=m&startDate={start_date}&endDate={end_date}"

        try:
            response = requests.get(url, timeout=15)

            if response.status_code == 200:
                records = response.json().get('observations', [])

                if records:
                    df = pd.DataFrame(records)

                    # Đảm bảo các cột cần thiết tồn tại trước khi xử lý
                    for col in ['valid_time_gmt', 'temp', 'rh', 'wspd', 'pressure', 'precip_total', 'wx_phrase', 'wx_icon']:
                        if col not in df.columns:
                            df[col] = pd.NA

                    df['Local_Time'] = pd.to_datetime(df['valid_time_gmt'], unit='s') + pd.Timedelta(hours=7)
                    df['weather_date'] = df['Local_Time'].dt.strftime('%Y-%m-%d')

                    daily = df.groupby('weather_date', as_index=False).agg(
                        temperature=('temp', 'mean'),
                        humidity=('rh', 'mean'),
                        precipitation=('precip_total', 'sum'),
                        wind_speed=('wspd', 'mean'),
                        pressure=('pressure', 'mean'),
                        wx_phrase=('wx_phrase', 'last'),
                        wx_icon=('wx_icon', 'last')
                    )

                    daily['province'] = province
                    daily['region'] = region
                    daily['weather_code'] = daily.apply(map_weather_code, axis=1)
                    daily['source'] = 'Weather.com API'

                    all_data.append(daily)
                    print(f"[OK] - Lấy được {len(daily)} ngày.")
                else:
                    print("[!] Không có dữ liệu.")
            else:
                print(f"[x] Lỗi API: {response.status_code}")

        except Exception as e:
            print(f"[x] Lỗi mạng hoặc kết nối: {e}")

        # Tránh bị API rate limit
        time.sleep(1.5)

# Gom dữ liệu, Chuẩn hóa và Xuất file
if all_data:
    final_df = pd.concat(all_data, ignore_index=True)
    final_df = final_df.sort_values(by=['province', 'weather_date']).reset_index(drop=True)

    # Chuyển đổi weather_code từ Số sang Chữ
    weather_mapping = {
        200: "Thunderstorms", 300: "Drizzle", 500: "Rain", 511: "Freezing Rain",
        520: "Heavy Rain", 521: "Showers", 600: "Snow", 602: "Blizzard",
        610: "Rain / Snow", 611: "Sleet", 621: "Snow Showers", 622: "Heavy Snow",
        711: "Smoke", 721: "Haze", 741: "Foggy", 751: "Dust / Sandstorm",
        781: "Windy", 800: "Clear", 801: "Mostly Clear", 802: "Partly Cloudy",
        803: "Mostly Cloudy", 804: "Cloudy", 906: "Hail", 999: "Not Available"
    }
    final_df['weather_code'] = final_df['weather_code'].map(weather_mapping).fillna('Unknown')

    # Làm tròn các cột số thập phân lấy 2 chữ số
    numeric_cols = ['temperature', 'humidity', 'precipitation', 'wind_speed', 'pressure']
    for col in numeric_cols:
        final_df[col] = pd.to_numeric(final_df[col], errors='coerce').round(2)

    # Chỉ lấy chính xác các cột được yêu cầu
    columns_to_keep = [
        'weather_date', 'province', 'region', 'temperature', 
        'humidity', 'precipitation', 'wind_speed', 'pressure', 
        'weather_code', 'source'
    ]
    final_df = final_df[columns_to_keep]

    # Xuất file cuối cùng
    file_name = 'south_weather_final.csv'
    final_df.to_csv(file_name, index=False, encoding='utf-8-sig')

    print(f"Hoàn tất Crawl, Dataset với {len(final_df)} dòng và {len(final_df.columns)} cột.")
    print(f"File lưu tại: '{file_name}'")
    print("\nThông tin bộ dữ liệu (5 dòng đầu):")
    print(final_df.head())
else:
    print("Không lấy được dữ liệu nào.")