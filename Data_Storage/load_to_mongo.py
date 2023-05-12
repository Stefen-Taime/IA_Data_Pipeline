from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, lit, col, from_json
from pyspark.sql.types import *

# Create a SparkSession
spark = SparkSession.builder \
    .appName("Data Processing") \
    .master("spark://spark:7077") \
    .getOrCreate()

# Define the list of cities
cities = ["Berlin", "London", "Madrid", "Paris", "Rome"]

# Define the schema
schema = StructType([
    StructField("airbnbHotels", ArrayType(
        StructType([
            StructField("thumbnail", StringType()),
            StructField("title", StringType()),
            StructField("subtitles", ArrayType(StringType())),
            StructField("price", StructType([
                StructField("currency", StringType()),
                StructField("value", DoubleType()),
                StructField("period", StringType())
            ])),
            StructField("rating", DoubleType()),
            StructField("link", StringType())
        ])
    ))
])

# Define the list of cities
cities = ["Berlin", "London", "Madrid", "Paris", "Rome"]

for city in cities:
    # Load the data for the current city
    df = spark.read.option("multiline", "true").json(f'hdfs://namenode:9000/input/{city}.json')

    
    # Add a new column with the city name
    df = df.withColumn("city", lit(city))

    # Explode the "airbnbHotels" field into separate rows
    df = df.select("city", explode(df.airbnbHotels).alias("airbnbHotels"))

    # Select the individual fields from the "airbnbHotels" objects
    df = df.select(
        lit(city).alias("city"),
        df.airbnbHotels.thumbnail.alias("thumbnail"),
        df.airbnbHotels.title.alias("title"),
        df.airbnbHotels.subtitles.alias("subtitles"),
        df.airbnbHotels.price.alias("price"),
        df.airbnbHotels.rating.alias("rating"),
        df.airbnbHotels.link.alias("link")
    )

    # Define MongoDB connection URI
    MONGODB_URI = "mongodb+srv://<username>:<password>@cluster0.td8y4zr.mongodb.net/?retryWrites=true&w=majority"

    # Write DataFrame to MongoDB
    df.write.format("com.mongodb.spark.sql.DefaultSource") \
        .mode("append") \
        .option("uri", MONGODB_URI) \
        .option("database", "booking") \
        .option("collection", "airbnb") \
        .save()

# Stop the SparkSession
spark.stop()
