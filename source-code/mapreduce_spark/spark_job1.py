from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, month

spark = (
    SparkSession.builder
    .appName("Spark Job 1 - National Monthly Average Temperature")
    .getOrCreate()
)

df = spark.read.csv(
    "/user/hadoop/weather_data_input/part-m-00000",
    header=True,
    inferSchema=True
)

trend_df = (
    df.groupBy(month("weather_date").alias("month"))
      .agg(avg("temperature").alias("avg_temperature"))
      .orderBy("month")
)


trend_df.write.mode("overwrite").csv(
    "/user/hadoop/spark_output/temp_trend",
    header=True
)

spark.stop()