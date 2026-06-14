from pyspark.sql import SparkSession
from pyspark.sql.functions import sum, avg, desc

spark = SparkSession.builder.appName("Spark Job 2 - Precipitation Analysis").getOrCreate()

df = spark.read.csv(
    "/user/hadoopgroup3/weather_data_input/part-m-00000", 
    header=False, 
    inferSchema=True
).toDF("weather_date", "province", "region", "temperature", "humidity", "precipitation", "wind_speed", "pressure", "weather_code", "source")

rain_analysis = df.groupBy("province", "region").agg(
    sum("precipitation").alias("total_precipitation"), 
    avg("precipitation").alias("avg_precipitation")
).orderBy(desc("total_precipitation"))

rain_analysis.show(20)

rain_analysis.coalesce(1).write.mode("overwrite").csv(
    "/user/hadoopgroup3/weather_spark_output/job2_output", 
    header=True
)
spark.stop()