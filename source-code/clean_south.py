import pandas as pd

INPUT_FILE = "south_weather.csv"
OUTPUT_FILE = "south_weather_clean.csv"

df = pd.read_csv(INPUT_FILE)

# Đổi tên cột
df = df.rename(columns={
    "Province": "province",
    "Date": "weather_date",
    "Temp_C_12h": "temperature",
    "Humidity_%_12h": "humidity",
    "Precipitation_mm_12h": "precipitation",
    "WindSpeed_kmh_12h": "wind_speed",
    "Pressure_mb_12h": "pressure",
    "Condition_12h": "weather_condition"
})

# Thêm region
df["region"] = "South"

# Thêm source
df["source"] = "South_API"

# Chỉ giữ cột chuẩn
df = df[
    [
        "province",
        "region",
        "weather_date",
        "temperature",
        "humidity",
        "precipitation",
        "wind_speed",
        "pressure",
        "weather_condition",
        "source"
    ]
]

# Chuyển ngày
df["weather_date"] = pd.to_datetime(
    df["weather_date"],
    errors="coerce"
)

# Loại bỏ trùng
df = df.drop_duplicates()

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print(f"Saved: {OUTPUT_FILE}")
print(df.head())