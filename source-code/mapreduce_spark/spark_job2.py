from pyspark.sql import SparkSession
from pyspark.sql.functions import sum, avg, col, desc

spark = SparkSession.builder.appName("Spark Job 2 - Precipitation Analysis").getOrCreate()

raw_df = spark.read.csv("/user/hadoop/weather_data_input/part-m-00000", header=False, inferSchema=True)
df = raw_df.toDF("weather_date", "province", "region", "temperature", "humidity", "precipitation", "wind_speed", "pressure", "weather_code", "source")

rain_analysis = df.groupBy("province", "region").agg(sum("precipitation").alias("total_precipitation"), avg("precipitation").alias("avg_precipitation")).orderBy(desc("total_precipitation"))
rain_analysis.show(20)
rain_analysis.write.mode("overwrite").csv("/user/hadoop/spark_output/rain_analysis", header=True)

spark.stop()