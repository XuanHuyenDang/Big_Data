from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, sum, col

spark = SparkSession.builder.appName("Spark Job 3 - Regional Weather Comparison").getOrCreate()

df = spark.read.csv("/user/hadoop/weather_data_input/part-m-00000", header=True, inferSchema=True)

regional_comparison = df.groupBy("region").agg(
    avg("temperature").alias("avg_temperature"), 
    avg("humidity").alias("avg_humidity"), 
    sum("precipitation").alias("total_precipitation"), 
    avg("wind_speed").alias("avg_wind_speed")
)
regional_comparison.show()
regional_comparison.write.mode("overwrite").csv("/user/hadoop/spark_output/regional_comparison", header=True)

spark.stop()