import pandas as pd

# Đọc các file đã được tiền xử lý và làm sạch
df_central = pd.read_csv('cleaned_central.csv')
df_north = pd.read_csv('cleaned_north.csv')
df_south = pd.read_csv('cleaned_south.csv')

# Hợp nhất dữ liệu bằng concat
df_final = pd.concat([df_central, df_north, df_south], ignore_index=True)

# Xuất ra file csv cuối cùng
df_final.to_csv('final_weather_data.csv', index=False)

print("Đã hợp nhất hoàn tất! File 'final_weather_data.csv' sạch 100% và sẵn sàng import vào MySQL.")