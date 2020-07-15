import tweepy
import logging
import time
import random
from datetime import datetime,timedelta
import os
from os import environ

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
def create_api():

    CONSUMER_KEY = environ['Consumer_key']
    CONSUMER_SECRET = environ['Consumer_secret']
    ACCESS_KEY = environ['Access_key']
    ACCESS_SECRET = environ['Access_secret']


    auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY,ACCESS_SECRET)
    api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("ERROR creating api",exc_info=True)
        raise e
    logger.info("Api created")
    return api
api = create_api()

def fav_tweets(api):
    print('Retrieving tweets ...........')
    mentions = api.mentions_timeline(tweet_mode="extended")
    for mention in reversed(mentions):
        if mention.in_reply_to_status_id is not None:
            return 
        if not mention.favorited:
            try:
                mention.favorite()
                logger.info(f"liked tweet by {mention.user.name}")
            except Exception as e:
                logger.error("Error on fav",exc_info=True)
        if not mention.retweeted:
            try:
                mention.retweet()
                logger.info(f"Retweeted tweet by {mention.user.name}")
            except Exception as e:
                logger.error("Error on fav and retweet",exc_info=True)
def fav_tweets_others(api,user_handle):
    search_query = f"{user_handle} -filter:retweets"
    logger.info(f"Retrieving tweets mentioning {user_handle}  ...")
    tweets = api.search(q=search_query)
    for tweet in tweets:
        print(tweet.in_reply_to_status_id,tweet.retweeted)
        # print(tweet['retweeted'])
        # print(tweet.__dict__['retweeted'])
        # print(tweet.__dict__._json.keys())
        if tweet.in_reply_to_status_id is not None:
            print("--------------------------------------------")
            return 
        if tweet.favorited == False:
            try:
                tweet.favorite()
                logger.info(f"liked tweet by {user_handle}")
            except Exception as e:
                logger.error("Error on fav",exc_info=True)
        if tweet.retweeted == False:
            try:
                tweet.retweet()
                logger.info(f"Retweeted tweet by {user_handle}")
            except Exception as e:
                logger.error("Error on fav and retweet",exc_info=True)
def follow_followers(api):
    logger.info("Retrieving and following followers")
    for follower in tweepy.Cursor(api.followers).items():
        if not follower.following:
            try:
                follower.follow()
                logger.info(f"Following {follower.name}")
            except tweepy.error.TweepError:
                pass
def unfollow(api,follower_id=None):
    if not follower_id:
        logger.info("Retrieving current followers")
        for following_id in tweepy.Cursor(api.friends).items():
                try:
                    api.destroy_friendship(following_id.id)
                    logger.info(f"Unfollowing {following_id.name}")
                except tweepy.error.TweepError:
                    pass
    else:
        try:
            api.destroy_friendship(follower_id)
            logger.info(f"Unfollowed {follower_id}...")
        except tweepy.error.TweepError:
            pass
# unfollow(api,"@ANI")
def retweet_hashtags(api,hash_tags):
    if type(hash_tags) is list:
        search_query = f"{hash_tags} -filter:retweets"
        tweets = api.search(q=search_query,tweet_mode="extended")
        for tweet in tweets:
            hashtags = [i['text'].lower() for i in tweet.__dict__['entities']['hashtags']]
            try:
                hash_tags=[hashtag.strip('#') for hashtag in hash_tags]
                hash_tags=list(hash_tags)
                # if set(hash_tags) & set(hashtags):
                if not tweet.retweeted:
                    api.retweet(tweet.id)
                    logger.info(f"Retweeted from {tweet.user.name} value {tweet.full_text}")
                    time.sleep(3)
            except tweepy.TweepError:
                logger.error("Error on retweet",exc_info=True)
    else:
        logger.error("Hashtags should be in a list",exc_info=True)
        return 
def tweet_daily(api,last_tweeted,text):
    if last_tweeted<datetime.now()-timedelta(hours=3):
        api.update_status(text)
        logger.info(f"Tweeted {text} at {datetime.now().strftime('%m/%d/%Y at %H:%M:%S')}")
        return datetime.now()
    else:
        return last_tweeted
def main():
    tweets =["happy","sad","hungry","angry"]
    api = create_api()
    last_tweeted=datetime.now()- timedelta(minutes=1)
    while True:
        fav_tweets_others(api,"@GunsagarSingh7")
        last_tweeted = tweet_daily(api,last_tweeted,random.choice(tweets))
        logger.info("waiting")
        time.sleep(30)
# main()
while True:
    fav_tweets_others(api,"@GunsagarSingh9")
    logger.info("Waiting")
    time.sleep(5)
# follow_followers(api)