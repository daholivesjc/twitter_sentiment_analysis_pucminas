# spark 
from pyspark.sql import SparkSession
from pyspark.sql.types import StringType, TimestampType, UserDefinedType
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
from helpers import (
    chart_tweets,
    pareto
)

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
    
# recent data
dataframe = spark.read.parquet(path+"/datasource/trusted/tweets_preprocessing")


## Tweets por candidato (em %)

candidatos = dataframe \
   .groupby('query') \
   .agg(F.expr('count(distinct twitter_id)').alias('qtde')) \
   .sort(F.col('qtde').desc()).select('query').rdd.flatMap(lambda x: x).collect()
   
tweets = dataframe \
   .groupby('query') \
   .agg(F.expr('count(distinct twitter_id)').alias('qtde')) \
   .sort(F.col('qtde').desc()).select('qtde').rdd.flatMap(lambda x: x).collect()


min_date = dataframe.agg({'created_at_tz': 'min'}).rdd.flatMap(lambda x: x).collect()[0]

max_date = dataframe.agg({'created_at_tz': 'max'}).rdd.flatMap(lambda x: x).collect()[0]

chart_tweets(
    x = candidatos,
    y = tweets,
    params = {
        "x": "query",
        "y": "qtde",
        "annotation_w":3e4,
        "annotation_h":8,
        "x_title": "% Tweets",
        "y_title": "candidatos",
        "title":f"Tweets por candidatos (em %) - ({min_date} - {max_date})"
    }    
)


features = dataframe.filter(F.col('query')=='lula').select('text_clean').rdd.flatMap(lambda x: x).collect()


from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation 
from time import time
from sklearn.model_selection import GridSearchCV

# LDA
tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=5000)
tf = tf_vectorizer.fit_transform(features)
tf_feature_names = tf_vectorizer.get_feature_names()

# Run LDA
t2 = time()
lda = LatentDirichletAllocation(
    n_components = 10, 
    random_state=0,
    n_jobs=-1,
    verbose=2
).fit(tf)
print("done in %0.3fs." % (time() - t2))

topic_list = []
for topic_idx, topic in enumerate(lda.components_):
        
    topic_dic = {}
    topic_dic["topic"] = topic_idx+1
    topic_dic["text"] = " ".join([tf_feature_names[i] for i in topic.argsort()[:-5 - 1:-1]])
    topic_list.append(topic_dic)



param_grid = {
    'doc_topic_prior': [0.001,0.1,0.5,0.9,1,10],
    'topic_word_prior': [0.001,0.1,0.5,0.9,1,10],
    'learning_method': ['batch','online'],
    'n_jobs': [-1],
    'verbose': [2]
}

grid_search = GridSearchCV(LatentDirichletAllocation(), param_grid, cv = 10 )#cv = cross validation
    
grid_search.get_params().keys()

grid_search.fit(tf)

grid_search.best_params_ 

print('Melhores parâmetros: ',grid_search.best_params_,'Melhor score: ', grid_search.best_score_,) 

7
# grafico geral
# qtde de tweets por source
# hashtags mais comuns por candidatos
# tweet com mais retweet por candidato
# tweet com mais like por candidato
# explicar uso do LDA para extracao de topicos
# tabelas dos 5 topicos mais comentados por candidato
# nuvens de palavras por candidato
#


dataframe.filter(F.col('query')=='lula').groupby('source').agg( F.count(F.col('twitter_id')).alias('qtde') ).sort(F.col('qtde').desc()).show(truncate=False)

dataframe.filter(F.col('query')=='lula').groupby('source').agg( F.count(F.col('twitter_id')).alias('qtde') ).sort(F.col('qtde').desc()).show(truncate=False)

dataframe.filter(F.col('query')=='bolsonaro').groupby('source').agg( F.count(F.col('twitter_id')).alias('qtde') ).sort(F.col('qtde').desc()).show(truncate=False)

dataframe.filter(F.col('query')=='sergio moro').groupby('source').agg( F.count(F.col('twitter_id')).alias('qtde') ).sort(F.col('qtde').desc()).show(truncate=False)



dataframe.filter(F.col('query')=='bolsonaro').groupby('hashtags_tag').agg( F.count(F.col('twitter_id')).alias('qtde') ).sort(F.col('qtde').desc()).show(truncate=False)

dataframe.filter(F.col('query')=='lula').groupby('text').agg( F.sum(F.col('retweet_count')).alias('qtde') ).sort(F.col('qtde').desc()).show(truncate=False)

dataframe.filter(F.col('query')=='lula').groupby('author_id').agg( F.count(F.col('twitter_id')).alias('qtde') ).sort(F.col('qtde').desc()).show(truncate=False)


dataframe.printSchema()





import re
text = "#promovolt #1st # promovolt #123"
re.findall(r'\B#\w*[a-zA-Z]+\w*', text)

    


    
    



