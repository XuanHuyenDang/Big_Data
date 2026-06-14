from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, month

spark = (
    SparkSession.builder
    .appName("Spark Job 1 - National Monthly Average Temperature")
    .getOrCreate()
)

# Đọc dữ liệu từ HDFS (dữ liệu do Sqoop đồng bộ)
df = spark.read.csv(
    "/user/hadoopgroup3/weather_data_input/part-m-00000",
    header=False,
    inferSchema=True
).toDF("weather_date", "province", "region", "temperature", "humidity", "precipitation", "wind_speed", "pressure", "weather_code", "source")

trend_df = (
    df.groupBy(month("weather_date").alias("month"))
      .agg(avg("temperature").alias("avg_temperature"))
      .orderBy("month")
)

# Lưu kết quả về HDFS
trend_df.coalesce(1).write.mode("overwrite").csv(
    "/user/hadoopgroup3/weather_spark_output/job1_output",
    header=True
)
spark.stop()