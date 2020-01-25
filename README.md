# UniHappyRanking

The end goal: A ranking of universities in the world by sentiment from Twitter. 

## Twitter Sentiment Analysis - University Students
This project is for analysing sentiments on student tweets about their universities, in order to build a 'happiness ranking'. 

To do that we first need the Twitter accounts of as many universities as we can. I have picked up a [dataset of the top 1000 universities](https://www.kaggle.com/mylesoneill/world-university-rankings), which of course doesn't have the Twitter accounts, so I had to use the Twitter Search API to try and match the university names to the account.

I have (almost) successfully found the Twitter handles, which you can find in the last column of the CSV [here](./world_rankings_with_twitter.csv). 

Out of the 1000 top universities, I have found matches for 879 of them, and 121 are without a match. Those with matches are not all entirely accurate, since some universities don't have Twitter accounts and my script picked up professors mentioning the school instead, or incorrect account due to non-English names and descriptions. But I'll keep working on it...

The source for the 1000 top universities in the world was the [Center for World University Rankings](http://cwur.org/).

Next is to get sentiment analysis in place, create a Jupyter notebook that proves a good classification accuracy of (positive, neutral, negative, irrelevant).

### The objective of this project is:
- [x] ~~Find tweets from students talking about their University~~
- [ ] Get the sentiment of those tweets
- [ ] Assign an average to each University
- [ ] Rank each University by the polarity
- [ ] Compare the 'happiness' ranking against the actual ranking : ) 
- [ ] Create a website that displays the data as an unofficial ranking of student happiness.
----