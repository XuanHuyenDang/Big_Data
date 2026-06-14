#!/usr/bin/env python3
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, corr, avg, count, round as spark_round, when, isnan

spark = SparkSession.builder \
    .appName("SPARK_JOB_4_TuongQuan_NhietDo_DoAm_TheoTinhVaMien") \
    .getOrCreate()

df = spark.read.csv(
    "/user/hadoopgroup3/weather_data_input/part-m-00000", 
    header=False, 
    inferSchema=True
).toDF("weather_date", "province", "region", "temperature", "humidity", "precipitation", "wind_speed", "pressure", "weather_code", "source")

# TÍNH TOÁN
province_result = df.groupBy("province", "region").agg(
    corr("temperature", "humidity").alias("correlation"),
    avg("temperature").alias("avg_temperature"),
    avg("humidity").alias("avg_humidity"),
    count("*").alias("num_days")
)

# Lọc nơi có đủ >= 30 ngày và đưa NaN về 0.0
province_result = province_result.filter(col("num_days") >= 30) \
    .withColumn("correlation", when(isnan(col("correlation")) | col("correlation").isNull(), 0.0).otherwise(col("correlation")))

# Làm tròn và sắp xếp
province_result = province_result.withColumn("correlation", spark_round(col("correlation"), 4)) \
    .withColumn("avg_temperature", spark_round(col("avg_temperature"), 2)) \
    .withColumn("avg_humidity", spark_round(col("avg_humidity"), 2)) \
    .orderBy(col("region"), col("correlation").desc())

print("KẾT QUẢ TOÀN QUỐC (Top 50 tỉnh):")
province_result.show(50, truncate=False)

output_path = "/user/hadoopgroup3/weather_spark_output/job4_output"

# Lưu kết quả
province_result.coalesce(1).write.mode("overwrite").option("header", "true").csv(output_path)
spark.stop()