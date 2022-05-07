# spark 
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from dateutil import tz
from dateutil import parser
from pyspark.sql.types import StringType, StructField, StructType, IntegerType, TimestampType
from datetime import timedelta
import unidecode
import re
import string
import nltk 
import os

path = os.path.abspath(os.path.join('..', ''))

# SPARK INSTANCE
spark = SparkSession.builder \
    .master("local[*]") \
    .config("spark.jars.packages", "io.delta:delta-core_2.12:1.1.0") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.executor.memory","8G") \
    .config("spark.driver.memory","8G") \
    .config("spark.executor.cores","12") \
    .getOrCreate()

# read twitter files
dataframe = spark.read.csv(path+"/datasource/twitter/*.csv", sep=';', header=True)

# remove duplicated
dataframe = dataframe.dropDuplicates(['text'])

# save tweets raw
(dataframe
 .write
 .option('mergeSchema', 'true')
 .option('overwriteSchema', 'true')
 .save(path+"/datasource/raw/tweets_v2", mode='overwrite')) 