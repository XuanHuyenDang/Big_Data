#!/usr/bin/env python3
import sys

if sys.version_info >= (3, 9):
    import collections.abc as collections_abc
    sys.modules.setdefault('collections.abc', collections_abc)

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count, month, when, round

spark = SparkSession.builder \
    .appName("Spark Job 5 - Xu hướng Lượng mưa theo Tháng") \
    .config("spark.executor.memory", "2g") \
    .config("spark.driver.memory", "2g") \
    .getOrCreate()

df = spark.read.option("header", "true").option("inferSchema", "true") \
    .csv("/user/hadoop/input_data/final_weather_data.csv")

df = df.withColumn("weather_date", col("weather_date").cast("date"))

monthly = df.withColumn("month", month("weather_date")) \
    .groupBy("region", "month") \
    .agg(
        round(avg("precipitation"), 2).alias("avg_rain_mm"),
        count(when(col("precipitation") >= 20, 1)).alias("heavy_rain_days"),
        count("*").alias("total_days")
    ) \
    .orderBy("region", "month")

monthly.show(40, truncate=False)

print("\n" + "="*90)
print("SO SÁNH LƯỢNG MƯA TRUNG BÌNH THEO THÁNG GIỮA 3 MIỀN")
print("="*90)

pivot = monthly.groupBy("month").pivot("region").avg("avg_rain_mm").orderBy("month")
pivot = pivot.select("month", 
                    round(col("Northern"), 2).alias("Northern"),
                    round(col("Central"), 2).alias("Central"),
                    round(col("Southern"), 2).alias("Southern"))
pivot.show(12, truncate=False)

# Lưu kết quả
monthly.coalesce(1).write.mode("overwrite").option("header", "true") \
    .csv("/user/hadoop/output/spark_job5")

print("\nJob 5 Success!")
print("Kết quả lưu tại: /user/hadoop/output/spark_job5")
spark.stop()
