#!/usr/bin/env python3
import sys
if sys.version_info >= (3, 9):
    import collections.abc as collections_abc
    sys.modules.setdefault('collections.abc', collections_abc)

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when, round, avg

spark = SparkSession.builder.appName("Spark Job 6 - Thời tiết Cực đoan").getOrCreate()

df = spark.read.csv(
    "/user/hadoopgroup3/weather_data_input/part-m-00000", 
    header=False, 
    inferSchema=True
).toDF("weather_date", "province", "region", "temperature", "humidity", "precipitation", "wind_speed", "pressure", "weather_code", "source")

extreme = df.withColumn("hot_day", when(col("temperature") >= 35, 1).otherwise(0)) \
            .withColumn("heavy_rain_day", when(col("precipitation") >= 30, 1).otherwise(0)) \
            .withColumn("strong_wind_day", when(col("wind_speed") >= 25, 1).otherwise(0)) \
            .withColumn("extreme_day", 
                when((col("temperature") >= 35) | (col("precipitation") >= 30) | (col("wind_speed") >= 25), 1).otherwise(0))

summary = extreme.groupBy("region").agg(
    count("*").alias("total_days"),
    count(when(col("extreme_day") == 1, 1)).alias("extreme_days"),
    round(avg(col("temperature")), 2).alias("avg_temp"),
    round(avg(col("precipitation")), 2).alias("avg_rain")
).withColumn("extreme_ratio_%", round(col("extreme_days") / col("total_days") * 100, 2))

summary.show(truncate=False)

summary.coalesce(1).write.mode("overwrite").option("header", "true").csv("/user/hadoopgroup3/weather_spark_output/job6_output")
spark.stop()