import numpy as np 
import pandas as pd 
import json
from pandas.io.json import json_normalize
import re
import nltk 
import matplotlib.pyplot as plt
import tweepy
import csv
import time
import os

auth = tweepy.OAuthHandler("", "")
auth.set_access_token("", "")

api = tweepy.API(auth, wait_on_rate_limit=True)

def jsonify_tweepy(tweepy_object):
    json_str = json.dumps(tweepy_object._json)
    return json.loads(json_str)

def ask_label(tweet):
    """
    Ask for label for this tweet. 
    """
    input("----\n\nTweet:%s\nPlease enter a label: <1: Positive, 2: Negative>" % tweet.text)

def find_tweets(uni):
    screen_name = uni['twitter_handle']
    print("Searching for @%s..." % uni['twitter_handle'])

    # Construct the results through pagination of the search API
    results = []

    # query_string = "(to:{screen_name}) (@{screen_name}) lang:en since:2015-01-01 -filter:links".format(screen_name=screen_name)
    query_string = "(to:{screen_name} OR @{screen_name}) lang:en -filter:links".format(screen_name=screen_name)

    for page in tweepy.Cursor(api.search, q=query_string, count=100, tweet_mode='extended').pages(5):
        results = results + page

    time.sleep(2)
    tweets = [jsonify_tweepy(tweet) for tweet in results]

    # print (tweets)
    df = json_normalize(tweets)
    print("Tweets found: %s" % len(df.index))

    # Filter out the tweets that are from the university itself, or don't have "student" in the user description.
    if ('user.screen_name' in df and 'user.description' in df):
        not_author = df['user.screen_name'] != uni['twitter_handle']
        student = df['user.description'] \
            .str \
            .contains("(student|alum|alumni|studying at|major|majoring|undergrad|postgrad|phd|sci|{screen_name}|{uni_name})" \
            .format(screen_name=uni['twitter_handle'], uni_name=uni['institution']), case=False, regex=True)

        print("Tweets not from uni author: %s" % len(df[not_author].index))
        print("Tweets with 'student' in desc: %s" % len(df[student].index))
        print("Tweets OK to use: %s" % len(df[student & not_author].index))
        df = df[not_author & student]

    # Write to file
    filename = uni['institution'].replace(' ', '_').lower()

    # Create dir if doesn't exist
    outdir = './tweets'
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    df.to_csv("tweets/%s.csv" % filename)
    df.to_html("tweets/%s.html" % filename)
    
def start_labelling(unis_df):
    """
    Begin searching for tweets and labelling
    """
    for index, row in unis_df.loc[547:].iterrows():
        print("index : {index}".format(index=index))
        if ('twitter_handle' in row):
            find_tweets(row)
        else:
            print("Skipped @%s, no Twitter account" % row['institution'])

unis_df = pd.read_csv('world_rankings_with_twitter.csv')
start_labelling(unis_df)