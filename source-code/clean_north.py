import pandas as pd

# =========================
# ĐỌC DỮ LIỆU
# =========================

INPUT_FILE = "north_weather.csv"
OUTPUT_FILE = "north_weather_clean.csv"

df = pd.read_csv(INPUT_FILE)

# =========================
# WEATHER CODE MAPPING
# =========================

weather_map = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",

    45: "Fog",
    48: "Rime Fog",

    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",

    61: "Light Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",

    71: "Light Snow",
    73: "Moderate Snow",
    75: "Heavy Snow",

    80: "Rain Showers",
    81: "Moderate Rain Showers",
    82: "Heavy Rain Showers",

    95: "Thunderstorm"
}

# =========================
# ĐỔI TÊN CỘT
# =========================

df = df.rename(columns={
    "date": "weather_date"
})

# =========================
# THÊM THÔNG TIN CHUNG
# =========================

df["region"] = "North"
df["source"] = "OpenMeteo"

# =========================
# CHUYỂN ĐỔI WEATHER CODE
# =========================

if "weather_condition" in df.columns:
    df["weather_condition"] = (
        df["weather_condition"]
        .map(weather_map)
        .fillna("Unknown")
    )

# =========================
# CHUYỂN KIỂU DỮ LIỆU
# =========================

df["weather_date"] = pd.to_datetime(
    df["weather_date"],
    errors="coerce"
)

numeric_columns = [
    "temperature",
    "humidity",
    "precipitation",
    "wind_speed",
    "pressure"
]

for col in numeric_columns:

    if col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

# =========================
# XỬ LÝ NULL
# =========================

for col in numeric_columns:

    if col in df.columns:

        df[col] = df[col].fillna(
            df[col].mean()
        )

# =========================
# XÓA BẢN GHI LỖI
# =========================

df = df.dropna(
    subset=["weather_date"]
)

# =========================
# LOẠI BỎ TRÙNG
# =========================

df = df.drop_duplicates()

# =========================
# LÀM TRÒN
# =========================

for col in numeric_columns:

    if col in df.columns:

        df[col] = df[col].round(2)

# =========================
# CHỌN CỘT CHUẨN
# =========================

final_columns = [
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

df = df[final_columns]

# =========================
# THỐNG KÊ
# =========================

print("\n===== THÔNG TIN DỮ LIỆU =====")
print("Số dòng:", len(df))
print("Số cột:", len(df.columns))

print("\nMissing values:")
print(df.isnull().sum())

print("\n5 dòng đầu:")
print(df.head())

# =========================
# LƯU FILE
# =========================

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print(f"\nĐã lưu: {OUTPUT_FILE}")