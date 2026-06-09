from pyspark.sql import SparkSession
from pyspark.sql.functions import sum, avg, col, desc

spark = SparkSession.builder.appName("Spark Job 2 - Precipitation Analysis").getOrCreate()

df = spark.read.csv("/user/hadoop/weather_data_input/part-m-00000", header=True, inferSchema=True)

rain_analysis = df.groupBy("province", "region").agg(
    sum("precipitation").alias("total_precipitation"), 
    avg("precipitation").alias("avg_precipitation")
).orderBy(desc("total_precipitation"))
rain_analysis.show(20)
rain_analysis.write.mode("overwrite").csv("/user/hadoop/spark_output/rain_analysis", header=True)

spark.stop()