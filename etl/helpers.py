from datetime import datetime, timedelta
import requests
import json
import pickle
import pandas as pd
import os
import glob


# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
# bearer_token = os.environ.get("BEARER_TOKEN")

def twitter_bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    BEARER_TOKEN = os.environ.get("BEARER_TOKEN")

    r.headers["Authorization"] = f"Bearer {BEARER_TOKEN}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r


def get_twitter_params(query, end_time):
    
    tweet_fields = [
        "author_id",
        "text",
        "created_at",
        "entities",
        "geo",
        "in_reply_to_user_id",
        "lang,possibly_sensitive",
        "referenced_tweets",
        "source",
        "public_metrics"]
 
    query_params = {
        "query": query,
        "tweet.fields": ",".join(tweet_fields), 
        "end_time": end_time,
        "max_results": 100
    }
        
    return query_params


def get_recents_tweets(logger, end_time, limit=10, query=""):
    
    logger.info(query)
    
    params = get_twitter_params(query, end_time)
    bearer_oauth = twitter_bearer_oauth
    search_url = os.environ.get("TWITTER_API_RECENT_SEARCH") 
    
    data_list = []
    data_dict = {}
    has_more = True
    count = 1
    while has_more:

        if count <= limit:
        
            r = requests.get(search_url, auth=bearer_oauth, params=params)
            response_dict = json.loads(r.text)
            
            logger.info(r.status_code)
            
            if response_dict["meta"]["result_count"] > 0:
                
                if response_dict["meta"].get('next_token',''):
                    
                    next_token = response_dict["meta"]["next_token"]
                    params["pagination_token"] = next_token
                
                    data_dict = {
                        "query": query,
                        "data": response_dict["data"],
                        "request_count": count
                    }
                
                    data_list.extend([data_dict])
                
                    count += 1
                
                else:
                    has_more = False
            
            else:
                has_more = False
        
        else:
            has_more = False
    
    return data_list


def save_tweets_file(tweet_list):

    path = os.path.abspath(os.path.join('..', '')) + "/datasource/raw_actual"
    
    timestamp = int((datetime.utcnow() - timedelta(minutes = 4)).timestamp()*1e3)
    
    with open(f"{path}/twitter_{timestamp}.lst", "wb") as fp:
        pickle.dump(tweet_list, fp)
      

def save_tweets_dataframe(dataframe, path_dataframe):

    path = os.path.abspath(os.path.join('..', '')) + "/datasource/raw_actual"
    
    timestamp = int((datetime.utcnow() - timedelta(minutes = 4)).timestamp()*1e3)
    
    # dataframe.to_pickle(f"{path}/dataframe/dataframe_{timestamp}.pkl")
    
    # dataframe.to_pickle(f"{path_dataframe}/dataframe_{timestamp}.pkl")
    
    dataframe.to_csv(f"{path_dataframe}/dataframe_{timestamp}.csv",encoding="utf-8", sep=";")
    
    print("Dataframe Tweets saved successfully!")
        


def read_tweet_files():

    path = os.path.abspath(os.path.join('..', '')) + "/datasource/raw_actual"
    
    files = glob.glob(f'{path}/*.lst', recursive = True)
    
    if not files:
        
        print("There are no files to be processed!")
        sys.exit()

    data_list = []
    data = {}
    for file in files:
        print(file)
        
        with open(file, "rb") as fp: 
            try:     
                file_data = pickle.load(fp)
                data_list.extend(file_data)
            except:
                pass
            
    twitter_list = []
    twitter_list_mentions = []
    twitter_list_annotations = []
    twitter_list_urls = []
    twitter_list_hashtags = []
    twitter_list_cashtags = []
    twitter_list_public_metrics = []
    twitter_list_referenced_tweets = []

    for twitter in data_list:
        for tweet in twitter["data"]:
        
            data = {
                "author_id": tweet["author_id"],
                "created_at": tweet["created_at"],
                "twitter_id": tweet["id"],
                "lang": tweet["lang"],
                "possibly_sensitive": tweet["possibly_sensitive"],
                "source": tweet["source"],
                "text": tweet["text"],
                "query": twitter["query"],
                "request_count": twitter["request_count"]
            }
               
            if tweet.get('referenced_tweets',''):
        
                for refer in tweet["referenced_tweets"]:
                    
                    referenced_tweets = {
                        "twitter_id": tweet["id"],
                        "referenced_tweets_type": refer["type"],
                        "referenced_tweets_id": refer["id"]
                    }
                    
                    twitter_list_referenced_tweets.append(referenced_tweets)
            
            if tweet.get('public_metrics',''):
                
                public_metrics = {
                    "twitter_id": tweet["id"],
                    "like_count": tweet["public_metrics"]["like_count"],
                    "quote_count": tweet["public_metrics"]["quote_count"],
                    "reply_count": tweet["public_metrics"]["reply_count"],
                    "retweet_count": tweet["public_metrics"]["retweet_count"]
                }
                
                twitter_list_public_metrics.append(public_metrics)
        
        
            if tweet.get('entities',''):
                
                if tweet["entities"].get('annotations',''):
                    
                    for annot in tweet["entities"].get('annotations',''):
                        
                        annotations = {
                            "twitter_id": tweet["id"],
                            "annotations_normalized_text": annot["normalized_text"],
                            "annotations_probability": annot["probability"],
                            "annotations_type": annot["type"]
                        }
                        
                        twitter_list_annotations.append(annotations)
                        
                if tweet["entities"].get('mentions',''):
                    
                    for ment in tweet["entities"].get('mentions',''):
                        
                        mentions = {
                            "twitter_id": tweet["id"],
                            "mentions_id": ment["id"],
                            "mentions_username": ment["username"]
                        }
                        
                        twitter_list_mentions.append(mentions)
        
                if tweet["entities"].get('urls',''):
            
                    for url in tweet["entities"].get('urls',''):
                        
                        urls = {
                            "twitter_id": tweet["id"],
                            "urls_display_url": url["display_url"],
                            "urls_expanded": url["expanded_url"],
                            "urls_url": url["url"]
                        }
            
                        twitter_list_urls.append(urls)
                        
                
                if tweet["entities"].get('hashtags',''):
            
                    for hashtag in tweet["entities"].get('hashtags',''):
                        
                        hashtags = {
                            "twitter_id": tweet["id"],
                            "hashtags_tag": hashtag["tag"]
                        }
            
                        twitter_list_hashtags.append(hashtags)
                
                if tweet["entities"].get('cashtags',''):
            
                    for cash in tweet["entities"].get('cashtags',''):
                        
                        cashtags = {
                            "twitter_id": tweet["id"],
                            "cashtags_tag": cash["tag"]
                        }
            
                        twitter_list_cashtags.append(cashtags)
        
            twitter_list.append(data)
            
    # dataframes
    df_twitter = pd.DataFrame(twitter_list)
    df_annotations = pd.DataFrame(twitter_list_annotations)
    df_cashtags = pd.DataFrame(twitter_list_cashtags)
    df_hashtags = pd.DataFrame(twitter_list_hashtags)
    df_mentions = pd.DataFrame(twitter_list_mentions)
    df_urls = pd.DataFrame(twitter_list_urls)
    df_public_metrics = pd.DataFrame(twitter_list_public_metrics)
    df_referenced_tweets = pd.DataFrame(twitter_list_referenced_tweets)
    
    # merge data
    if not df_annotations.empty:
        dataframe = df_twitter.merge(df_annotations,how="left",on="twitter_id")
    
    if not df_cashtags.empty:
        dataframe = dataframe.merge(df_cashtags,how="left",on="twitter_id")
        
    if not df_hashtags.empty:
        dataframe = dataframe.merge(df_hashtags,how="left",on="twitter_id")
        
    if not df_mentions.empty:  
        dataframe = dataframe.merge(df_mentions,how="left",on="twitter_id")
        
    if not df_urls.empty:    
        dataframe = dataframe.merge(df_urls,how="left",on="twitter_id")
        
    if not df_public_metrics.empty:    
        dataframe = dataframe.merge(df_public_metrics,how="left",on="twitter_id")
        
    if not df_referenced_tweets.empty:    
        dataframe = dataframe.merge(df_referenced_tweets,how="left",on="twitter_id")
        
    delete_tweets_file(files)   
    
    print("Files with successfully processed Tweets!")
    
    return dataframe

def delete_tweets_file(files):
    
    for file in files:
        
        try:
            os.remove(file)
        except:
            pass
        

