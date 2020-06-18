import tweepy
import json
import datetime
import random
import requests
import logging 
import Wallpaper
import schedule
import time
import os
import sys
from os import environ


consumer_key = environ['API_key']
consumer_secret_key = environ['API_secret_key']
access_token = environ['access_token']
access_token_secret = environ['access_token_secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret_key)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

logger=logging.getLogger()
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.DEBUG) 

def get_daily_quote():
    URL = "https://quotes.rest/qod?language=en"
    response = requests.get(URL)
    res = json.loads(response.text)
    return res['contents']['quotes'][0]['quote'] + " ~" + res['contents']['quotes'][0]['author']

def select_file():
    path =r'quotes'
    files = os.listdir(path)
    index = random.randrange(0, len(files))
    return os.path.join(path, files[index])

def get_quotes():
    fileName=select_file()
    with open(fileName,encoding="utf8") as f:
        quotes_json = json.load(f)
    return quotes_json

def get_random_quote():
    quotes = get_quotes()
    random_quote = random.choice(quotes)
    return random_quote

def create_tweet():
    quote = get_random_quote()
    tweet = """{}~{}""".format(quote['quote'], quote['author'])
    return tweet

def get_hashtag():
    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    hashtags = {0: "#SundayThoughts #qod", 1: "#MondayMotivation #qod", 2: "#TuesdayThoughts #qod", 3: "#WednesdayWisdom #qod",
                4: "#ThursdayThoughts #qod", 5: "#FeelGoodFriday #qod", 6: "#SaturdayVibes #qod"}
    now = datetime.datetime.now()
    day = now.strftime("%A")
    index = days.index(day)
    return hashtags.get(index)

def get_last_tweet(file):
    f=open(file,'r')
    lastId=int(f.read().strip())
    f.close()
    return lastId    


def put_last_tweet(file,Id):
    f=open(file,'w')
    f.write(str(Id))
    f.close()
    return

def respondToTweet(file='tweet_IDs.txt'):
    last_id=get_last_tweet(file)
    mentions=api.mentions_timeline(last_id,tweet_mode='extended')
    if len(mentions)==0:
        return
    new_id=0
    logger.info("someone mentioned me...")
    for mention in reversed(mentions):
        print(str(mention.id) + '-' + mention.full_text)
        new_id=mention.id
        if '#qod' in mention.full_text.lower():
            print("Responding back with QOD to -{}".format(mention.id))
            tweet = create_tweet()
            Wallpaper.get_wallpaper(tweet)
        
            # Upload image
            media = api.media_upload("pil_text.png")
            try:
                logger.info("liking and replying to tweet")
                api.create_favorite(mention.id)
                api.update_status('@'+mention.user.screen_name +" Here's your #qod",mention.id, media_ids=[media.media_id])
            except:
                logger.info('Error occured in replying to mentioned tweets')
                print("Already sent to {}".format(mention.id))
    put_last_tweet(file,new_id)

def weekendTweet():
    logger.info('Inside weekend tweet')
    try:
        tweet = create_tweet() + "\n" + get_hashtag()
        if len(tweet) > 280:
            logger.info("Failed, max tweet length reached")
            return 
        api.update_status(tweet)
        logger.info('SENT weekend tweet...')
        return "Success- Weekend Tweet Sent"
    except tweepy.TweepError as e:
        logger.info('Error occured in daily tweet')
        return e.response.text


def tweet_quote():
    logger.info('Inside daily tweet function')
    try:
        tweet = get_daily_quote() + "\n" + get_hashtag()
        if len(tweet) > 280:
            logger.info("Failed, max tweet length reached")
            return 
        api.update_status(tweet)
        logger.info('SENT daily tweet...')
        return "Success"
    
    except tweepy.TweepError as e:
        logger.info('Error occured in daily tweet')
        return e.response.text

schedule.every().day.at("07:00").do(tweet_quote)
schedule.every().sunday.at("12:00").do(weekendTweet)
schedule.every().saturday.at("10:00").do(weekendTweet)
schedule.every(1).minutes.do(respondToTweet) 
while True:
    schedule.run_pending() 
    time.sleep(1) 
