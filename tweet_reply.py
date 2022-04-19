import tweepy
import json
import datetime
import random
import requests
import logging
import schedule
import time
import os
from os import environ
import Wallpaper, instagram, instaQuote

consumer_key = environ['API_key']
consumer_secret_key = environ['API_secret_key']
access_token = environ['access_token']
access_token_secret = environ['access_token_secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret_key)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)


def get_daily_quote():
    URL = "https://quotes.rest/qod?language=en"
    try:
        logger.info('Hitting URL to get tweet...')
        response = requests.get(URL)
    except:
        logger.info('Failure occurred in hitting URL')
        return ""
    res = json.loads(response.text)
    return res['contents']['quotes'][0]['quote'] + "\n~" + res['contents']['quotes'][0]['author']

def get_quote_via_api():
    url = "https://api.quotable.io/random"

    try:
        response = requests.get(url)
    except:
        logger.info("Error while calling API...")

    res = json.loads(response.text)
    print(res)
    return res['content'] + "-" + res['author']

def select_file():
    path = r'quotes'
    files = os.listdir(path)
    index = random.randrange(0, len(files))
    return os.path.join(path, files[index])


def get_quote_via_file():
    fileName = select_file()
    with open(fileName, encoding="utf8") as f:
        quotes_json = json.load(f)
    return quotes_json


def get_random_quote_via_file():
    quotes = get_quote_via_file()
    random_quote = random.choice(quotes)
    return random_quote


def create_tweet():
    quote = get_random_quote_via_file()
    tweet = """{}\n~{}""".format(quote['quote'], quote['author'])
    return tweet


def get_last_tweet(file):
    f = open(file, 'r')
    lastId = int(f.read().strip())
    f.close()
    return lastId


def put_last_tweet(file, Id):
    f = open(file, 'w')
    f.write(str(Id))
    f.close()
    return


def respondToTweet(file='tweet_IDs.txt'):
    last_id = get_last_tweet(file)
    mentions = api.mentions_timeline(last_id)
    if len(mentions) == 0:
        return
    new_id = 0
    logger.info("someone mentioned me...")
    for mention in reversed(mentions):
        print(str(mention.id) + '-' + mention.full_text)
        new_id = mention.id
        if '#qod' in mention.full_text.lower():
            print("Responding back with QOD to -{}".format(mention.id))
            tweet = get_quote_via_api()
            Wallpaper.create_wallpaper(tweet)

            # Upload image
            media = api.media_upload("pil_text.png")
            try:
                logger.info("liking and replying to tweet")
                api.create_favorite(mention.id)
                api.update_status('@' + mention.user.screen_name + " Here's your Quote \n#qod", mention.id,
                                  media_ids=[media.media_id])
            except:
                logger.info('Error occurred in replying to mentioned tweets')
                print("Already sent to {}".format(mention.id))
    put_last_tweet(file, new_id)
    

def weekend_tweet():
    logger.info('Inside weekend tweet')
    try:
        text = get_quote_via_api()
        tweet = text + "\n#qod"
        if len(tweet) > 280:
            logger.info("Failed, max tweet length reached")
            return
        api.update_status(tweet)
        logger.info('SENT weekend tweet...✔')
        return "Success"
    except tweepy.TweepError as e:
        logger.info('Error occurred in weekend tweet')
        return e.response.text


def daily_tweet():
    logger.info('Inside daily tweet function')
    try:
        quote = get_daily_quote()
        if len(quote) < 5:
            logger.info('Did not receive any tweet')
            return weekendTweet()   # If daily tweet fails call weekend tweet
        tweet = quote + "\n#qod"
        if len(tweet) > 280:
            logger.info("Failed, max tweet length reached")
            return weekendTweet()   # If daily tweet fails call weekend tweet
        api.update_status(tweet)
        logger.info('SENT daily tweet...✔')
        return "Success"
    except tweepy.TweepError as e:
        logger.info('Error occurred in daily tweet')
        return e.response.text


def schedule_next_instagram():
   time_str = '{:02d}:{:02d}'.format(random.randint(10, 23), random.randint(0, 59))
   schedule.clear()
   print("Scheduled instagram today for {}".format(time_str))
   schedule.every().day.at(time_str).do(instagram.upload_wallpaper)


schedule.every().day.at("06:00").do(daily_tweet)
schedule.every().saturday.at("12:00").do(weekend_tweet)
schedule.every().sunday.at("09:00").do(weekend_tweet)
schedule.every(1).minutes.do(respondToTweet)
schedule_next_instagram()
while True:
    schedule.run_pending()
    time.sleep(1)
