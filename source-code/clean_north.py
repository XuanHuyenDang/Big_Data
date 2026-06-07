import pandas as pd

def remove_accents_by_replace(text):
    text = str(text)
    accents = {
        'a': 'á|à|ả|ã|ạ|ă|ắ|ằ|ẳ|ẵ|ặ|â|ấ|ầ|ẩ|ẫ|ậ', 'd': 'đ', 'e': 'é|è|ẻ|ẽ|ẹ|ê|ế|ề|ể|ễ|ệ',
        'i': 'í|ì|ỉ|ĩ|ị', 'o': 'ó|ò|ỏ|õ|ọ|ô|ố|ồ|ổ|ỗ|ộ|ơ|ớ|ờ|ở|ỡ|ợ', 'u': 'ú|ù|ủ|ũ|ụ|ư|ứ|ừ|ử|ữ|ự',
        'y': 'ý|ỳ|ỷ|ỹ|ỵ', 'A': 'Á|À|Ả|Ã|Ạ|Ă|Ắ|Ằ|Ẳ|Ẵ|Ặ|Â|Ấ|Ầ|Ẩ|Ẫ|Ậ', 'D': 'Đ',
        'E': 'É|È|Ẻ|Ẽ|Ẹ|Ê|Ế|Ề|Ể|Ễ|Ệ', 'I': 'Í|Ì|Ỉ|Ĩ|Ị', 'O': 'Ó|Ò|Ỏ|Õ|Ọ|Ô|Ố|Ồ|Ổ|Ỗ|Ộ|Ơ|Ớ|Ờ|Ở|Ỡ|Ợ',
        'U': 'Ú|Ù|Ủ|Ũ|Ụ|Ư|Ứ|Ừ|Ử|Ữ|Ự', 'Y': 'Ý|Ỳ|Ỷ|Ỹ|Ỵ'
    }
    for non_accent, accented_chars in accents.items():
        for char in accented_chars.split('|'):
            text = text.replace(char, non_accent)
    return text.strip()

def map_north_weather_code(code):
    mapping = {
        '0': 'Clear', '1': 'Mostly Clear', '2': 'Partly Cloudy', '3': 'Overcast',
        '45': 'Fog', '48': 'Depositing Rime Fog',
        '51': 'Light Drizzle', '53': 'Moderate Drizzle', '55': 'Dense Drizzle',
        '56': 'Light Freezing Drizzle', '57': 'Dense Freezing Drizzle',
        '61': 'Light Rain', '63': 'Moderate Rain', '65': 'Heavy Rain',
        '66': 'Light Freezing Rain', '67': 'Heavy Freezing Rain',
        '71': 'Slight Snow Fall', '73': 'Moderate Snow Fall', '75': 'Heavy Snow Fall',
        '77': 'Snow Grains',
        '80': 'Slight Rain Showers', '81': 'Moderate Rain Showers', '82': 'Violent Rain Showers',
        '85': 'Slight Snow Showers', '86': 'Heavy Snow Showers',
        '95': 'Thunderstorm', '96': 'Thunderstorm with Hail', '99': 'Heavy Thunderstorm with Hail'
    }
    try:
        # Chuyển về số nguyên rồi mới thành chuỗi để tránh lỗi "80.0" -> "80"
        clean_code = str(int(float(code))) 
        return mapping.get(clean_code, 'Unknown')
    except:
        return 'Unknown'

# 1. Đọc dữ liệu
df = pd.read_csv('north_weather.csv')

# 2. Đổi tên cột và định dạng ngày
df = df.rename(columns={'date': 'weather_date', 'weather_condition': 'weather_code'})
df['weather_date'] = pd.to_datetime(df['weather_date']).dt.strftime('%Y-%m-%d')

# 3. Chuẩn hóa tên tỉnh thành
df['province'] = df['province'].apply(remove_accents_by_replace)

# 4. Thêm/Cập nhật cột bị thiếu và vùng miền
df['region'] = 'Northern'
df['source'] = 'Open-meteo.com'
df['weather_code'] = df['weather_code'].apply(map_north_weather_code)

# 5. Xử lý Outliers & Missing values
df = df.dropna(subset=['temperature', 'humidity'])
df['temperature'] = df['temperature'].clip(lower=-5, upper=50)
df['humidity'] = df['humidity'].clip(lower=0, upper=100)
df['precipitation'] = df['precipitation'].clip(lower=0)

# 6. Xóa dòng trùng lặp
df = df.drop_duplicates(subset=['weather_date', 'province'])
# 7. Làm tròn số thập phân
numeric_cols = ['temperature', 'humidity', 'precipitation', 'wind_speed', 'pressure']
df[numeric_cols] = df[numeric_cols].round(2)
# 8. Sắp xếp cột và lưu file
target_columns = ['weather_date', 'province', 'region', 'temperature', 'humidity', 'precipitation', 'wind_speed', 'pressure', 'weather_code', 'source']
df = df[target_columns]
df.to_csv('cleaned_north.csv', index=False)
print("Đã làm sạch xong file Miền Bắc: cleaned_north.csv")