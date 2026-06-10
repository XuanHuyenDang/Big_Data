#!/usr/bin/env python3
import sys

if sys.version_info >= (3, 9):
    import collections.abc as collections_abc
    sys.modules.setdefault('collections.abc', collections_abc)

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when, round, avg

spark = SparkSession.builder \
    .appName("Spark Job 6 - Phân tích Thời tiết Cực đoan theo Miền") \
    .config("spark.executor.memory", "2g") \
    .config("spark.driver.memory", "2g") \
    .getOrCreate()

df = spark.read.option("header", "true").option("inferSchema", "true") \
    .csv("/user/hadoop/input_data/final_weather_data.csv")

extreme = df.withColumn("hot_day", when(col("temperature") >= 35, 1).otherwise(0)) \
            .withColumn("heavy_rain_day", when(col("precipitation") >= 30, 1).otherwise(0)) \
            .withColumn("strong_wind_day", when(col("wind_speed") >= 25, 1).otherwise(0)) \
            .withColumn("extreme_day", 
                when((col("temperature") >= 35) | 
                     (col("precipitation") >= 30) | 
                     (col("wind_speed") >= 25), 1).otherwise(0))

result = extreme.groupBy("province", "region").agg(
    count("*").alias("total_days"),
    count(when(col("hot_day") == 1, 1)).alias("hot_days"),
    count(when(col("heavy_rain_day") == 1, 1)).alias("heavy_rain_days"),
    count(when(col("strong_wind_day") == 1, 1)).alias("strong_wind_days"),
    count(when(col("extreme_day") == 1, 1)).alias("extreme_days")
).withColumn("extreme_ratio", round(col("extreme_days") / col("total_days") * 100, 2))

result = result.orderBy(col("region"), col("extreme_ratio").desc())

result.show(33, truncate=False)

print("\n" + "="*85)
print("TỔNG HỢP THEO MIỀN")
print("="*85)

summary = extreme.groupBy("region").agg(
    count("*").alias("total_days"),
    count(when(col("extreme_day") == 1, 1)).alias("extreme_days"),
    round(avg(col("temperature")), 2).alias("avg_temp"),
    round(avg(col("precipitation")), 2).alias("avg_rain")
).withColumn("extreme_ratio_%", round(col("extreme_days") / col("total_days") * 100, 2))

summary.show(truncate=False)

# Lưu kết quả
result.coalesce(1).write.mode("overwrite").option("header", "true") \
    .csv("/user/hadoop/output/spark_job6")

print("\n Spark Job 6 Success!")
print("Kết quả lưu tại: /user/hadoop/output/spark_job6")
spark.stop()
