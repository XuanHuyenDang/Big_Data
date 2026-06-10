#!/usr/bin/env python3

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, corr, avg, count, round as spark_round, when, isnan

spark = SparkSession.builder \
    .appName("SPARK_JOB_4_TuongQuan_NhietDo_DoAm_TheoTinhVaMien") \
    .config("spark.executor.memory", "4g") \
    .config("spark.driver.memory", "2g") \
    .getOrCreate()
df = spark.read.option("header", "true").option("inferSchema", "true") \
    .csv("/user/hadoop/input_data/final_weather_data.csv")

# TÍNH TOÁN
province_result = df.groupBy("province", "region").agg(
    corr("temperature", "humidity").alias("correlation"),
    avg("temperature").alias("avg_temperature"),
    avg("humidity").alias("avg_humidity"),
    count("*").alias("num_days")
)

# Xử lý an toàn: Lọc nơi có đủ >= 30 ngày và đưa NaN về 0.0
province_result = province_result.filter(col("num_days") >= 30) \
    .withColumn("correlation", when(isnan(col("correlation")) | col("correlation").isNull(), 0.0).otherwise(col("correlation")))

# Làm tròn và sắp xếp
province_result = province_result.withColumn("correlation", spark_round(col("correlation"), 4)) \
    .withColumn("avg_temperature", spark_round(col("avg_temperature"), 2)) \
    .withColumn("avg_humidity", spark_round(col("avg_humidity"), 2)) \
    .orderBy(col("region"), col("correlation").desc())

region_result = df.groupBy("region").agg(
    corr("temperature", "humidity").alias("correlation"),
    avg("temperature").alias("avg_temperature"),
    avg("humidity").alias("avg_humidity"),
    count("*").alias("num_days")
)

region_result = region_result.withColumn("correlation", when(isnan(col("correlation")) | col("correlation").isNull(), 0.0).otherwise(col("correlation"))) \
    .withColumn("correlation", spark_round(col("correlation"), 4)) \
    .withColumn("avg_temperature", spark_round(col("avg_temperature"), 2)) \
    .withColumn("avg_humidity", spark_round(col("avg_humidity"), 2)) \
    .orderBy("correlation")

#HIỂN THỊ KẾT QUẢ 
print("SPARK JOB 4 - TƯƠNG QUAN NHIỆT ĐỘ & ĐỘ ẨM THEO TỈNH / MIỀN")

print("\nKẾT QUẢ THEO MIỀN (Tổng quan Vĩ mô):")
region_result.show(truncate=False)

print("\n" + "="*80)
print("KẾT QUẢ TOÀN QUỐC (Top 50 tỉnh):")
print("="*80)
province_result.show(50, truncate=False)

output_path = "/user/hadoop/output/spark_job4"

# Lưu kết quả cấp tỉnh
province_result.coalesce(1).write.mode("overwrite").option("header", "true") \
    .csv(output_path)

print(f"\nJob 4 Success!")
print(f"Kết quả cấp tỉnh đã được lưu tại: {output_path}")
spark.stop()
