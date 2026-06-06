import requests
import pandas as pd
import urllib3

# Tắt cảnh báo SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.trust_env = False

# =========================
# MIỀN BẮC
# =========================

provinces = [
    {
        "province": "Ha Noi",
        "latitude": 21.0285,
        "longitude": 105.8542
    },
    {
        "province": "Hai Phong",
        "latitude": 20.8449,
        "longitude": 106.6881
    },
    {
        "province": "Quang Ninh",
        "latitude": 20.9712,
        "longitude": 107.0448
    },
    {
        "province": "Lao Cai",
        "latitude": 22.4809,
        "longitude": 103.9755
    }
]

# =========================
# THỜI GIAN
# =========================

start_date = "2025-01-01"
end_date = "2025-12-31"

# =========================
# BIẾN DỮ LIỆU CẦN LẤY
# =========================

daily_variables = [
    "temperature_2m_mean",
    "relative_humidity_2m_mean",
    "precipitation_sum",
    "wind_speed_10m_max",
    "surface_pressure_mean",
    "weather_code"
]

all_data = []

# =========================
# GỌI API
# =========================

for province in provinces:

    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": province["latitude"],
        "longitude": province["longitude"],
        "start_date": start_date,
        "end_date": end_date,
        "daily": ",".join(daily_variables),
        "timezone": "Asia/Ho_Chi_Minh"
    }

    try:

        response = session.get(
            url,
            params=params,
            verify=False,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        if "daily" not in data:
            print(f"Không có dữ liệu: {province['province']}")
            continue

        df_city = pd.DataFrame(data["daily"])

        df_city["province"] = province["province"]

        all_data.append(df_city)

        print(f"Đã lấy dữ liệu: {province['province']}")

    except Exception as e:
        print(f"Lỗi {province['province']}: {e}")

# =========================
# GỘP DỮ LIỆU
# =========================

df = pd.concat(all_data, ignore_index=True)

# =========================
# ĐỔI TÊN CỘT
# =========================

df = df.rename(columns={
    "time": "date",
    "temperature_2m_mean": "temperature",
    "relative_humidity_2m_mean": "humidity",
    "precipitation_sum": "precipitation",
    "wind_speed_10m_max": "wind_speed",
    "surface_pressure_mean": "pressure",
    "weather_code": "weather_condition"
})

# =========================
# LƯU FILE CSV
# =========================

df.to_csv(
    "north_weather.csv",
    index=False,
    encoding="utf-8-sig"
)

print(f"\nĐã lưu {len(df)} bản ghi vào north_weather.csv")