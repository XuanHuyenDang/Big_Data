import pandas as pd

north = pd.read_csv("north_weather_clean.csv")
central = pd.read_csv("central_weather_clean.csv")
south = pd.read_csv("south_weather_clean.csv")

weather = pd.concat(
    [north, central, south],
    ignore_index=True
)

weather = weather.drop_duplicates()

weather.to_csv(
    "weather_clean.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Total records:", len(weather))
print(weather.head())