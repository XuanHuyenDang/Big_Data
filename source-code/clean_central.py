import pandas as pd

def remove_accents_by_replace(text):
    """Chuẩn hóa bằng cách thay thế trực tiếp từng ký tự có dấu"""
    text = str(text)
    # Có thể thêm các lệnh replace từ viết tắt tại đây nếu cần
    text = text.replace("TP.HCM", "Ho Chi Minh")
    
    # Từ điển ánh xạ thay thế
    accents = {
        'a': 'á|à|ả|ã|ạ|ă|ắ|ằ|ẳ|ẵ|ặ|â|ấ|ầ|ẩ|ẫ|ậ',
        'd': 'đ',
        'e': 'é|è|ẻ|ẽ|ẹ|ê|ế|ề|ể|ễ|ệ',
        'i': 'í|ì|ỉ|ĩ|ị',
        'o': 'ó|ò|ỏ|õ|ọ|ô|ố|ồ|ổ|ỗ|ộ|ơ|ớ|ờ|ở|ỡ|ợ',
        'u': 'ú|ù|ủ|ũ|ụ|ư|ứ|ừ|ử|ữ|ự',
        'y': 'ý|ỳ|ỷ|ỹ|ỵ',
        'A': 'Á|À|Ả|Ã|Ạ|Ă|Ắ|Ằ|Ẳ|Ẵ|Ặ|Â|Ấ|Ầ|Ẩ|Ẫ|Ậ',
        'D': 'Đ',
        'E': 'É|È|Ẻ|Ẽ|Ẹ|Ê|Ế|Ề|Ể|Ễ|Ệ',
        'I': 'Í|Ì|Ỉ|Ĩ|Ị',
        'O': 'Ó|Ò|Ỏ|Õ|Ọ|Ô|Ố|Ồ|Ổ|Ỗ|Ộ|Ơ|Ớ|Ờ|Ở|Ỡ|Ợ',
        'U': 'Ú|Ù|Ủ|Ũ|Ụ|Ư|Ứ|Ừ|Ử|Ữ|Ự',
        'Y': 'Ý|Ỳ|Ỷ|Ỹ|Ỵ'
    }
    
    for non_accent, accented_chars in accents.items():
        for char in accented_chars.split('|'):
            text = text.replace(char, non_accent)
            
    return text.strip()

# 1. Đọc dữ liệu
df = pd.read_csv('central_weather_2025.csv')

# 2. Đổi tên cột và định dạng ngày
df = df.rename(columns={'datetime': 'weather_date'})
df['weather_date'] = pd.to_datetime(df['weather_date']).dt.strftime('%Y-%m-%d')

# 3. Chuẩn hóa tên tỉnh thành (Dùng hàm thay thế)
df['province'] = df['province'].apply(remove_accents_by_replace)

# 4. Cập nhật tên vùng miền
df['region'] = 'Central'

# 5. Chuẩn hóa Weather Code 
df['weather_code'] = df['weather_code'].astype(str).str.title()

# 6. Xử lý Outliers & Missing values
df = df.dropna(subset=['temperature', 'humidity'])
df['temperature'] = df['temperature'].clip(lower=-5, upper=50)
df['humidity'] = df['humidity'].clip(lower=0, upper=100)
df['precipitation'] = df['precipitation'].clip(lower=0)

# 7. Loại bỏ dòng trùng lặp
df = df.drop_duplicates(subset=['weather_date', 'province'])

# 8. Làm tròn các cột số thập phân về 2 chữ số
numeric_cols = ['temperature', 'humidity', 'precipitation', 'wind_speed', 'pressure']
df[numeric_cols] = df[numeric_cols].round(2)
# 9. Sắp xếp cột và lưu file
target_columns = ['weather_date', 'province', 'region', 'temperature', 'humidity', 'precipitation', 'wind_speed', 'pressure', 'weather_code', 'source']
df = df[target_columns]
df.to_csv('cleaned_central.csv', index=False)
print("Đã làm sạch xong file Miền Trung: cleaned_central.csv")