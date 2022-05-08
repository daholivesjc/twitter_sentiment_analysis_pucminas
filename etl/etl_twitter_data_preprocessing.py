# spark 
from pyspark.sql import SparkSession
from pyspark.sql.types import StringType, TimestampType
import pyspark.sql.functions as F

# date tools
from dateutil import tz
from dateutil import parser
from datetime import timedelta

# string tools
import unidecode
import re
import string
import nltk 

# operational system tool
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

# set sao paulo time zone
to_zone = tz.gettz('America/Sao_Paulo')

def text_preprocessing(instancia):

    punct = string.punctuation
    trantab = str.maketrans(punct, len(punct)*' ')
    
    instancia = instancia.lower()
    instancia = re.sub('\d+', '', str(instancia)).replace("&gt;"," ").replace("&lt;"," ") 
    instancia = re.sub(r"https?:\/\/\S+","", instancia)
    instancia = re.sub(r"@[A-Za-z0-9\w]+","", instancia)
    instancia = re.sub(r"#[A-Za-z0-9\w]+","", instancia)
    instancia = re.sub('^RT ',' ',instancia)
    instancia = re.sub(r"http\S+", "", instancia) 
    instancia = re.sub(r'([A-Za-z])\1{2,}', r'\1', instancia)
    instancia = instancia.translate(trantab).replace("\n"," ")
    instancia = unidecode.unidecode(instancia)

    # #Lista de  stopwords no idioma portugues
    stopwords = [unidecode.unidecode(w) for w in list(set(nltk.corpus.stopwords.words('portuguese')))]

    # #guarda no objeto palavras
    palavras = [i for i in instancia.split() if not i in stopwords]
    
    palavras = [re.sub(r'(ha)\1+', r'\1',word) for word in palavras]
    palavras = [re.sub(r'(uha)\1+', r'\1',word) for word in palavras]

    palavras = " ".join(palavras) \
        .strip() \
        .replace('"','') \
        .replace('.','') \
        .replace('-','') \
        .replace('_','') \
        .replace('*','') \
        .replace('>','') \
        .replace('<','') \
        .replace('!','') \
        .replace('?','') \
        .replace('[','') \
        .replace(']','') \
        .replace('\'','') \
        .replace('rt ','')

    return "-" if palavras.strip()=="" else palavras.strip()

convert_date = F.udf(
    lambda x: parser.isoparse(x).replace(tzinfo=to_zone).replace(tzinfo=None) - timedelta(hours=3),
    TimestampType()               
)

preprocessing = F.udf(
    lambda x: text_preprocessing(x),
    StringType()               
)

# recent data
dataframe = spark.read.parquet(path+"/datasource/raw/tweets")

# filter portugueses tweets
dataframe = dataframe.filter(F.col('lang')=='pt')
    
# adjust created_at to datetime
dataframe = dataframe.withColumn('created_at_tz', F.to_date(convert_date(F.col('created_at')),'yyyy-MM-dd') )

# have retweets
dataframe = dataframe.withColumn('have_retweet', 
   F.when(F.col("retweet_count")>0, 1).otherwise(0)
)

# have likes
dataframe = dataframe.withColumn('have_like', 
   F.when(F.col("like_count")>0, 1).otherwise(0)
)

# cleaning text
dataframe = dataframe.withColumn('text_clean', preprocessing(F.col('text')) )

# filter 
dataframe = dataframe.filter(F.col("text_clean")!="-")

# drop duplicates
dataframe = dataframe.dropDuplicates(['text_clean'])

# 14/03/2022 a 18/03/2022 e 21/03/2022 a 25/03/2022
dataframe = dataframe \
    .filter(F.col('created_at_tz').between('2022-03-14 00:00:00','2022-03-25 00:00:00')) \
    .filter(F.dayofweek(F.col('created_at_tz')).between(2,6)) \
    .filter(F.col('query').isNotNull()) \
    .drop('_c0',
          'possibly_sensitive',
          'request_count',
          'annotations_normalized_text',
          'annotations_probability',
          'annotations_type',
          'mentions_id',
          'mentions_username',
          'urls_display_url',
          'urls_expanded',
          'urls_url',
          'referenced_tweets_type',
          'referenced_tweets_id')

# select columns and filter na values from like_count to 0
dataframe = dataframe.select(
    F.col('author_id'),
    F.to_timestamp(convert_date(F.col('created_at')),'yyyy-MM-dd 00:00:00').alias('created_at'),
    F.col('twitter_id'),
    F.col('lang'),
    F.col('source'),
    F.col('text'),
    F.col('query'),
    F.col('hashtags_tag'),
    F.col('like_count').cast('int'),
    F.col('reply_count').cast('int'),
    F.col('retweet_count').cast('int'),
    F.col('created_at_tz'),
    F.col('text_clean'),
).na.fill(value=0,subset=['like_count','reply_count','retweet_count'])

# save data
(dataframe
 .write
 .option('mergeSchema', 'true')
 .option('overwriteSchema', 'true')
 .save(path+"/datasource/trusted/tweets_preprocessing", mode='overwrite')) 



df = spark.read.parquet(path+"/datasource/trusted/tweets_preprocessing")


df.select(F.col('twitter_id')).distinct().count()








