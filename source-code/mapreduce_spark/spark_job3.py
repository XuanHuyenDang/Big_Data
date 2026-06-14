from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, sum

spark = SparkSession.builder.appName("Spark Job 3 - Regional Weather Comparison").getOrCreate()

df = spark.read.csv(
    "/user/hadoopgroup3/weather_data_input/part-m-00000", 
    header=False, 
    inferSchema=True
).toDF("weather_date", "province", "region", "temperature", "humidity", "precipitation", "wind_speed", "pressure", "weather_code", "source")

regional_comparison = df.groupBy("region").agg(
    avg("temperature").alias("avg_temperature"), 
    avg("humidity").alias("avg_humidity"), 
    sum("precipitation").alias("total_precipitation"), 
    avg("wind_speed").alias("avg_wind_speed")
)

regional_comparison.show()

regional_comparison.coalesce(1).write.mode("overwrite").csv(
    "/user/hadoopgroup3/weather_spark_output/job3_output", 
    header=True
)
spark.stop()