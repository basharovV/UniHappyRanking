# UniHappyRanking

A ranking of universities in the world by sentiment from Twitter. 

## Twitter Sentiment Analysis - University Students

This project is for analysing sentiments on student tweets about their universities, in order to build a 'happiness ranking'.

> **_NOTE:_**  This project is for the data science element, the front-end part of the project is in [this repository](https://github.com/basharovV/UniHappyRanking-Web).

### The objective of this project is:
- [x] ~~Find tweets from students talking about their University~~
- [x] Get the sentiment of those tweets
- [x] Assign a happiness ranking to each University
- [x] Rank each University by the happiness
- [ ] Compare the 'happiness' ranking against the actual ranking : ) 
- [x] Create a website that displays the data as an unofficial ranking of student happiness. Check it out [here](https://uni-happy-ranking.herokuapp.com)
----

### Finding the Twitter accounts of universities
First need the Twitter accounts of as many universities as we can. I have picked up a [dataset of the top 1000 universities](https://www.kaggle.com/mylesoneill/world-university-rankings), which of course doesn't have the Twitter accounts, so I had to use the Twitter Search API to try and match the university names to the account. 

I have (almost) successfully found the Twitter handles, which you can find in the last column of the CSV [here](./world_rankings_with_twitter.csv). 

Out of the 1000 top universities, I have found matches for 879 of them, and 121 are without a match. Those with matches are not all entirely accurate, since some universities don't have Twitter accounts and my script picked up professors mentioning the school instead, or incorrect account due to non-English names and descriptions. But I'll keep working on it...

The source for the 1000 top universities in the world was the [Center for World University Rankings](http://cwur.org/).

### Fetching tweets for every university
Once we have the Twitter accounts, we can fetch tweets for every university. The tweets we're interested in should match the following criteria:
1. Tweet is from an account that is _not_ the university itself.
2. Tweet mentions the @<university>, or replies to it
3. Tweet is from an account that could be a student (i.e contains "student, grad, major, etc" in profile description)
4. Tweet is plain text, no links
5. Tweet is in English

Using [Tweepy](https://github.com/tweepy/tweepy) we can perform this search with an advanced query that looks like this:

```js
results = []

query_string = "(to:{screen_name} OR @{screen_name}) lang:en -filter:links".format(screen_name=screen_name)

for page in tweepy.Cursor(api.search, q=query_string, count=100, tweet_mode='extended').pages(5):
        results = results + page
```

Tweets for every university are saved in a CSV in the /tweets-data folder.

### Performing sentiment analysis

Although I could have manually labelled all the tweets myself with 'positive', 'negative', I decided to skip ahead and use another labelled dataset from NLTK, and saved the trained model from NLTK to then classify the tweets I fetched. 
```
nltk.download('twitter_samples')
```
You can find the pre-trained model at [/sentiment-analysis/sentiment_classifier.picke](./sentiment-analysis/sentiment_classifier.picke)

For every tweet I ran the classification, and assigned a new column "sentiment". I then counted the total count, positive count and negative count and assigned these columns to the original CSV (university ranking).

### Cleaning up
Although all the tweets were classified, some universities didn't have much Twitter activity, so I filtered out those that have < 50 tweets. 

### Assigning a happiness ranking
This is simply counting the number of positive tweets / total tweets for each uni. We then sort by descending and we get our ranking of happiness! 

happiness_rank | world_rank | institution | country | national_rank
--- | --- | --- | --- | ---
1 | 150	| McMaster University	| Canada | 6
2 | 229	| Laval University |	Canada | 11
3 | 33	| University of Illinois at Urbana–Champaign |	USA	| 24
4 | 824	| University of Brighton | United Kingdom |	61
5 | 399 |	University of Nebraska Medical Center	| USA	| 136
6 | 122 |	Aarhus University	| Denmark	| 2
7 | 448 |	Indian Institute of Science	| India	| 3
8 | 42 | McGill University	| Canada| 2
9 | 130	| University of New South Wales	| Australia |	4
10 | 240	| University of Leicester	| United Kingdom	| 19

Interesting results! 

### Congratulations McMaster University 🥳 

----

### Considerations
- The data sucks. Sorry McMaster University, you're probably not the happiest university in the world. However! I aim to improve this by feeding in Student Room form posts and other sources as well. If you have any suggestions on how to make this ranking more than just an experiment, let me know! 
- Sentiment analysis is very basic, doesn't have context, or humor, sarcasm understanding.

If you would like to contribute, please submit an issue :) 
