import pandas as pd

def remove_accents_by_replace(text):
    """Hàm loại bỏ dấu tiếng Việt thủ công"""
    text = str(text)
    text = text.replace("TP.HCM", "Ho Chi Minh")
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

# def map_south_weather_code(code):
#     """Hàm dịch mã thời tiết của Wunderground/OpenWeatherMap sang chữ"""
#     try:
#         c = int(float(code))
#         if c == 800: return 'Clear'
#         elif 801 <= c <= 802: return 'Partly Cloudy'
#         elif 803 <= c <= 804: return 'Overcast'
#         elif 200 <= c < 300: return 'Thunderstorm'
#         elif 300 <= c < 400: return 'Drizzle'
#         elif 500 <= c < 600: return 'Moderate Rain'
#         else: return 'Unknown'
#     except:
#         return 'Unknown'

# 1. Đọc dữ liệu (File Wunderground cũ)
df = pd.read_csv('south_weather.csv', encoding='ansi')

# 2. Định dạng ngày 
# LƯU Ý: File gốc đã có sẵn cột 'weather_date' nên không cần lệnh rename như file API nữa
df['weather_date'] = pd.to_datetime(df['weather_date']).dt.strftime('%Y-%m-%d')

# 3. Chuẩn hóa tên tỉnh thành
df['province'] = df['province'].apply(remove_accents_by_replace)

# 4. Cập nhật vùng miền và DỊCH MÃ THỜI TIẾT (từ 80x sang Text)
df['region'] = 'Southern'
df['weather_code'] = df['weather_code']

# 5. Xử lý Outliers & Missing values
df = df.dropna(subset=['temperature', 'humidity'])
df['temperature'] = df['temperature'].clip(lower=-5, upper=50)
df['humidity'] = df['humidity'].clip(lower=0, upper=100)
df['precipitation'] = df['precipitation'].clip(lower=0)

# 6. Xóa dòng trùng lặp
df = df.drop_duplicates(subset=['weather_date', 'province'])

# 7. Làm tròn số thập phân về 2 chữ số
numeric_cols = ['temperature', 'humidity', 'precipitation', 'wind_speed', 'pressure']
df[numeric_cols] = df[numeric_cols].round(2)

# 8. Sắp xếp cột và lưu file
target_columns = ['weather_date', 'province', 'region', 'temperature', 'humidity', 'precipitation', 'wind_speed', 'pressure', 'weather_code', 'source']
df = df[target_columns]
df.to_csv('cleaned_south.csv', index=False)
print("Đã làm sạch xong file Miền Nam: cleaned_south.csv")