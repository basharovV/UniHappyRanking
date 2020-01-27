from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import twitter_samples, stopwords
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk import FreqDist, classify, NaiveBayesClassifier
import pickle
import re, string, random
import sys
import os
import pandas as pd
import glob
import numpy as np

def remove_noise(tweet_tokens, stop_words = ()):

    cleaned_tokens = []

    for token, tag in pos_tag(tweet_tokens):
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
        token = re.sub("(@[A-Za-z0-9_]+)","", token)

        if tag.startswith("NN"):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'

        lemmatizer = WordNetLemmatizer()
        token = lemmatizer.lemmatize(token, pos)

        if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
            cleaned_tokens.append(token.lower())
    return cleaned_tokens

def get_all_words(cleaned_tokens_list):
    for tokens in cleaned_tokens_list:
        for token in tokens:
            yield token

def get_tweets_for_model(cleaned_tokens_list):
    for tweet_tokens in cleaned_tokens_list:
        yield dict([token, True] for token in tweet_tokens)

def train_and_save():
    positive_tweets = twitter_samples.strings('positive_tweets.json')
    negative_tweets = twitter_samples.strings('negative_tweets.json')
    text = twitter_samples.strings('tweets.20150430-223406.json')
    tweet_tokens = twitter_samples.tokenized('positive_tweets.json')[0]

    stop_words = stopwords.words('english')

    positive_tweet_tokens = twitter_samples.tokenized('positive_tweets.json')
    negative_tweet_tokens = twitter_samples.tokenized('negative_tweets.json')

    positive_cleaned_tokens_list = []
    negative_cleaned_tokens_list = []

    for tokens in positive_tweet_tokens:
        positive_cleaned_tokens_list.append(remove_noise(tokens, stop_words))

    for tokens in negative_tweet_tokens:
        negative_cleaned_tokens_list.append(remove_noise(tokens, stop_words))

    all_pos_words = get_all_words(positive_cleaned_tokens_list)

    freq_dist_pos = FreqDist(all_pos_words)
    print(freq_dist_pos.most_common(10))

    positive_tokens_for_model = get_tweets_for_model(positive_cleaned_tokens_list)
    negative_tokens_for_model = get_tweets_for_model(negative_cleaned_tokens_list)

    positive_dataset = [(tweet_dict, "Positive")
                         for tweet_dict in positive_tokens_for_model]

    negative_dataset = [(tweet_dict, "Negative")
                         for tweet_dict in negative_tokens_for_model]

    dataset = positive_dataset + negative_dataset

    random.shuffle(dataset)

    train_data = dataset[:7000]
    test_data = dataset[7000:]

    classifier = NaiveBayesClassifier.train(train_data)
    f = open('sentiment_classifier.pickle', 'wb')
    pickle.dump(classifier, f)

    print("Accuracy is:", classify.accuracy(classifier, test_data))

    print(classifier.show_most_informative_features(10))

class SentimentClassifier():

    def __init__(self, folder):
        self.folder = folder
        f = open('sentiment-analysis/sentiment_classifier.pickle', 'rb')
        self.classifier = pickle.load(f)
        self.universities_by_sentiment = pd.read_csv('university-rankings-data/world_rankings_with_twitter.csv')
        self.sentiments = pd.DataFrame(columns=['total', 'positive', 'negative', 'university'])
        self.result = None
        print(self.universities_by_sentiment)
        f.close()

    def get_uni_name_from_filename(self, filename):
        return filename.lower().replace('_', ' ').replace('.csv', '').replace("{0}/".format(self.folder), '').title()

    def classify_single(self, tweet):
        """
        Process a single tweet and classify it
        """
        text = tweet.full_text
        custom_tokens = remove_noise(word_tokenize(text))
        sentiment = self.classifier.classify(dict([token, True] for token in custom_tokens))
        return self.classifier.classify(dict([token, True] for token in custom_tokens))

    def classify_tweets(self, uni_name, filename):
        tweets = pd.read_csv(os.path.join(self.folder, filename))
        count = len(tweets.index)
        positive = 0
        negative = 0
        if (count > 0):
            print("Classifying tweets for {0}".format(os.path.join(self.folder, filename)))

            # Get sentiments for this university
            sentiments = tweets.apply(self.classify_single, axis=1)
            if (len(sentiments) > 0):
                # Count how many positive and negative
                positive = sentiments.where(lambda x: x.str.lower() == "positive").count()
                negative = sentiments.where(lambda x: x.str.lower() == "negative").count()
                print ("Total : {0} | Positive: {1} | Negative: {2}".format(count, positive, negative))

        self.sentiments = self.sentiments.append(pd.DataFrame({'total': [count], 'positive': [positive], 'negative': [negative], 'university': [uni_name]}, columns=['total', 'positive', 'negative', 'university']), ignore_index=True)
        
    def classify_folder(self):
        # First load the list of unis from the original csv
        unis = pd.read_csv('university-rankings-data/world_rankings_with_twitter.csv')
        
        for index, uni in unis.iterrows():
            self.classify_tweets(uni['institution'], "{0}.csv".format(uni['institution'].lower().replace(' ', '_')))
        
        self.result = pd.concat([self.universities_by_sentiment, self.sentiments], axis=1, sort=False)
        
        positive_fraction = self.result['positive'].divide(self.result['total'].where(self.result['total'] != 0, np.nan))
        print("happiness ranking: {0}".format(positive_fraction))
        self.result['happiness_ranking'] = positive_fraction
        self.result.to_csv("sentiment-analysis/universities_by_sentiment")

def process_files():
    # Iterate over all the tweets and add a new column "Sentiment" using pd
    classifier = SentimentClassifier("tweets-data")
    classifier.classify_folder()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == 'train':
            train_and_save()
        elif sys.argv[1] == 'classify':
            process_files()
        else:
            print ('Example usage: labeller.py [train/classify]')
            sys.exit(2)
    else:
        print ('Example usage: labeller.py [train/classify]')
        sys.exit(2)