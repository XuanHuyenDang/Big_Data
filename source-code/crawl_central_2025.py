import sys
import subprocess
import pandas as pd
import numpy as np

from meteostat import Hourly

from datetime import datetime

from concurrent.futures import ThreadPoolExecutor, as_completed

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

required_packages = [
    "pandas",
    "numpy",
    "meteostat"
]

for pkg in required_packages:
    try:
        __import__(pkg)
    except:
        install(pkg)

START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 12, 31)

OUTPUT_FILE = "central_weather_2025.csv"

locations = [

    {
        "province": "Huế",
        "region": "Central Vietnam",
        "station": "48852"
    },

    {
        "province": "Đà Nẵng",
        "region": "Central Vietnam",
        "station": "48855"
    },

    {
        "province": "Gia Lai",
        "region": "Central Highlands Vietnam",
        "station": "48866"
    },

    {
        "province": "Khánh Hòa",
        "region": "South Central Coast",
        "station": "48877"
    }

]

weather_map = {
    1: "Clear",
    2: "Fair",
    3: "Cloudy",
    4: "Overcast",
    5: "Fog",
    6: "Freezing Fog",
    7: "Light Rain",
    8: "Rain",
    9: "Heavy Rain",
    10: "Freezing Rain",
    11: "Heavy Freezing Rain",
    12: "Sleet",
    13: "Heavy Sleet",
    14: "Light Snowfall",
    15: "Snowfall",
    16: "Heavy Snowfall",
    17: "Rain Shower",
    18: "Heavy Rain Shower",
    19: "Sleet Shower",
    20: "Heavy Sleet Shower",
    21: "Snow Shower",
    22: "Heavy Snow Shower",
    23: "Lightning",
    24: "Hail",
    25: "Thunderstorm",
    26: "Heavy Thunderstorm",
    27: "Storm"
}

def process_location(loc):

    try:

        print(f"Đang crawl: {loc['province']}")

        # LẤY DỮ LIỆU THEO GIỜ
        data = Hourly(
            loc["station"],
            START_DATE,
            END_DATE
        ).fetch()

        if data is None or data.empty:
            print(f"Không có dữ liệu: {loc['province']}")
            return pd.DataFrame()

        data = data.reset_index()

        # GIỮ CỘT CẦN LẤY
        data["date"] = data["time"].dt.date

        # GROUP THEO NGÀY
        daily = data.groupby("date").agg({
            "temp": "mean",
            "rhum": "mean",
            "prcp": "sum",
            "wspd": "mean",
            "pres": "mean",
            "coco": lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan
        }).reset_index()

        # TẠO DATAFRAME
        df = pd.DataFrame()

        df["datetime"] = pd.to_datetime(
            daily["date"]
        ).dt.strftime("%Y-%m-%d")

        df["province"] = loc["province"]

        df["region"] = loc["region"]

        # Nhiệt độ trung bình
        df["temperature"] = daily["temp"]

        # HUMIDITY trung bình
        df["humidity"] = daily["rhum"]

        # Lượng mưa
        df["precipitation"] = daily["prcp"]

        # Gió
        df["wind_speed"] = daily["wspd"]

        # Áp suất
        df["pressure"] = daily["pres"]

        # WEATHER CODE
        df["weather_code"] = daily["coco"].map(weather_map)

        df["source"] = "Meteostat Hourly"

        # CLEAN NULL
        numeric_cols = [
            "temperature",
            "humidity",
            "precipitation",
            "wind_speed",
            "pressure"
        ]

        for col in numeric_cols:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

            df[col] = df[col].interpolate()

            df[col] = df[col].fillna(
                df[col].mean()
            )

            df[col] = df[col].round(2)

        # weather_code null
        df["weather_code"] = df["weather_code"].fillna("Unknown")

        print(f"Hoàn tất: {loc['province']}")

        return df

    except Exception as e:

        print(f"Lỗi {loc['province']}: {e}")

        return pd.DataFrame()

all_dfs = []

print("START WEATHER PIPELINE")

with ThreadPoolExecutor(max_workers=4) as executor:

    futures = [

        executor.submit(process_location, loc)

        for loc in locations

    ]

    for future in as_completed(futures):

        result = future.result()

        if not result.empty:
            all_dfs.append(result)

if len(all_dfs) == 0:

    print("\nKHÔNG LẤY ĐƯỢC DỮ LIỆU!")

    sys.exit()

df = pd.concat(
    all_dfs,
    ignore_index=True
)

# SORT
df = df.sort_values(
    by=["province", "datetime"]
)

df = df.reset_index(drop=True)

# SAVE CSV
df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("DONE!")

print(f"\nFile: {OUTPUT_FILE}")

print(f"Số dòng dữ liệu: {len(df)}")

print("\nSample Data:\n")

print(df.head())