import pandas as pd

INPUT_FILE = "central_weather_2025.csv"
OUTPUT_FILE = "central_weather_clean.csv"

df = pd.read_csv(INPUT_FILE)

# Đổi tên cột
df = df.rename(columns={
    "datetime": "weather_date"
})

# weather_code -> weather_condition
df["weather_condition"] = df["weather_code"]

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