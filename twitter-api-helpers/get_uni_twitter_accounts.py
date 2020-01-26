import tweepy
import csv
import numpy as np
import pandas as pd
import time
import progressbar

auth = tweepy.OAuthHandler("=", "")
auth.set_access_token("", "")

api = tweepy.API(auth)

# Twitter can only allow 900 request per 15 minute window (1 req/ second) for /searchusers, so let's set an interval

interval = 1.1 # seconds

bar = progressbar.ProgressBar(max_value=1000, redirect_stdout=True)
def get_alt_name(uni):
    """ 
    Return the alternative name for a university. 
    Eg. University of Cambridge -> Cambridge University
    :name:  
    """
    if ('university of' in uni['institution'].lower()):
        sides = uni['institution'].split('of') # ['university', 'cambridge']
        alt_order = np.roll(np.array(sides), -1) # ['cambridge', 'university']
        return ' '.join(alt_order.tolist()).strip().title() # Cambridge University
    return None

def twitter_handle_find(uni):
    
    """
    Find the Twitter handle for a university by name

    Go through all the universities and
    Match to Twitter handle if
    1. There's only 1 result
    2. It's a verified account
    2. OR there is an exact match on the name
    3. Or there is a fuzzy match on the name
    4. Or there is a fuzzy match on the description
    """

    uni_name = uni['institution']
    alt_name = uni['institution_alt']
    
    print('Searching for %s' % uni_name)
    bar.update(uni.name)

    time.sleep(interval) # WAIT FOR 2 SECS

    # Search on Twitter 
    page = api.search_users(q=uni_name, page=1, count=10)
    
    # If single result, return the handle
    if (len(page) == 1):
        return page[0].screen_name

    # Return first if verified
    if (len(page) > 0 and page[0].verified):
        # print ("Matched by verified ✔️")
        return page[0].screen_name

    # Or first exact match of the name (by comparison)
    matches_name = [uni for uni in page if uni_name == uni.name]
    # print ("Matches by exact name: ", len(matches_name))

    if (len(matches_name) > 0):
        return matches_name[0].screen_name
    
    # Or first exact match of the alt name (by comparison)
    if (uni['institution_alt'] != None):
        matches_alt_name = [uni for uni in page if alt_name == uni.name]
        # print ("Matches by alt name: ", len(matches_alt_name))

        if (len(matches_alt_name) > 0):
            return matches_alt_name[0].screen_name

    # Or first exact match of the name (by contains)
    matches_in_name = [uni for uni in page if uni_name in uni.name]
    # print ("Matches by name: ", len(matches_in_name))

    if (len(matches_in_name) > 0):
        return matches_in_name[0].screen_name

    # Or first match in description (by contains)
    matches_in_description = [uni for uni in page if uni_name in uni.description]
    # print ("Matches by description: ", len(matches_in_description))

    if (len(matches_in_description) > 0):
        return matches_in_description[0].screen_name
    # Or none
    return None

# Read DataFrame from the file
times_rankings_df = pd.read_csv("world_rankings_2015.csv") # All

print("Adding alternative name...")

# Add column for alternative name
times_rankings_df['institution_alt'] = times_rankings_df.apply(get_alt_name, axis=1)

print(times_rankings_df)
print("Adding Twitter handles...")
# Add missing column twitter_handle by searching the Twitter API
twitter_handles = times_rankings_df.apply(twitter_handle_find, axis=1)

# Add the new column
times_rankings_df['twitter_handle'] = twitter_handles

print("Twitter handles added:")
print(times_rankings_df[['institution','twitter_handle']])

print("Writing to file: world_rankings_with_twitter.csv")

times_rankings_df.to_csv("world_rankings_with_twitter.csv")
