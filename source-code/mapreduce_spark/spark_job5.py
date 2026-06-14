#!/usr/bin/env python3
import sys
if sys.version_info >= (3, 9):
    import collections.abc as collections_abc
    sys.modules.setdefault('collections.abc', collections_abc)

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count, month, when, round

spark = SparkSession.builder.appName("Spark Job 5 - Xu hướng Lượng mưa").getOrCreate()

df = spark.read.csv(
    "/user/hadoopgroup3/weather_data_input/part-m-00000", 
    header=False, 
    inferSchema=True
).toDF("weather_date", "province", "region", "temperature", "humidity", "precipitation", "wind_speed", "pressure", "weather_code", "source")

df = df.withColumn("weather_date", col("weather_date").cast("date"))

monthly = df.withColumn("month", month("weather_date")) \
    .groupBy("region", "month") \
    .agg(
        round(avg("precipitation"), 2).alias("avg_rain_mm"),
        count(when(col("precipitation") >= 20, 1)).alias("heavy_rain_days"),
        count("*").alias("total_days")
    ).orderBy("region", "month")

pivot = monthly.groupBy("month").pivot("region").avg("avg_rain_mm").orderBy("month")
pivot = pivot.select("month", 
                     round(col("Northern"), 2).alias("Northern"),
                     round(col("Central"), 2).alias("Central"),
                     round(col("Southern"), 2).alias("Southern"))

pivot.show(12, truncate=False)

monthly.coalesce(1).write.mode("overwrite").option("header", "true").csv("/user/hadoopgroup3/weather_spark_output/job5_output")
spark.stop()