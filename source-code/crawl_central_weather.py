import sys
import subprocess
import pandas as pd
import numpy as np

from meteostat import Daily

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

START_DATE = datetime(2026, 1, 1)
END_DATE = datetime(2026, 6, 1)

OUTPUT_FILE = "central_weather.csv"

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

def process_location(loc):

    try:

        print(f"Đang crawl: {loc['province']}")

        # tạo point
        data = Daily(
            loc["station"],
            START_DATE,
            END_DATE
        ).fetch()
        print(data.head())
        # kiểm tra dữ liệu
        if data is None or data.empty:
            print(f"Không có dữ liệu: {loc['province']}")
            return pd.DataFrame()

        data = data.reset_index()
        # TẠO DATAFRAME
        df = pd.DataFrame()

        df["datetime"] = data["time"].dt.strftime("%Y-%m-%d")

        df["province"] = loc["province"]

        df["region"] = loc["region"]

        # nhiệt độ trung bình ngày
        df["temperature"] = data["tavg"]

        # humidity không có trong daily
        df["humidity"] = None

        # lượng mưa
        df["precipitation"] = data["prcp"]

        # tốc độ gió
        df["wind_speed"] = data["wspd"]

        # áp suất
        df["pressure"] = data["pres"]

        # tạo weather label theo precipitation
        df["precipitation"] = df["precipitation"].fillna(0)
        conditions = [
            (df["precipitation"] > 20),
            (df["precipitation"] > 5),
            (df["precipitation"] > 0)
        ]

        choices = [
            "Heavy Rain",
            "Rain",
            "Light Rain"
        ]

        df["weather_code"] = np.select(
            conditions,
            choices,
            default="Clear"
        )

        df["source"] = "Meteostat Daily"
        
        # CLEAN NULL VALUES
        numeric_cols = [
            "temperature",
            "precipitation",
            "wind_speed",
            "pressure"
        ]

        for col in numeric_cols:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

            # interpolate
            df[col] = df[col].interpolate()

            # fill remaining null
            df[col] = df[col].fillna(
                df[col].mean()
            )

            # round
            df[col] = df[col].round(2)

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

# SORT DATA
df = df.sort_values(
    by=["province", "datetime"]
)

df = df.reset_index(drop=True)

# SAVE TO CSV
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
