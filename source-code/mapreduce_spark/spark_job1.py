from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, col

spark = SparkSession.builder \
    .appName("Spark Job 1 - Temperature Trend Analysis") \
    .getOrCreate()

df = spark.read.csv("/user/hadoop/weather_data_input/part-m-00000", header=True, inferSchema=True)

trend_df = df.groupBy("weather_date") \
             .agg(avg("temperature").alias("avg_temperature")) \
             .orderBy("weather_date")

trend_df.show(35)
trend_df.write.mode("overwrite").csv("/user/hadoop/spark_output/temp_trend", header=True)
spark.stop()