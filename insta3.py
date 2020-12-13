import logging
import os
import random
import time
from os import environ

import mmh3
import praw
import re
import requests
from bitarray import bitarray
from instabot import Bot

import hashtag

insta_user_name = environ['INSTA_NAME']
insta_pass = environ['INSTA_PASS']

clientId = environ['REDDIT_CLIENT_ID']
clientSecret = environ['REDDIT_CLIENT_SECRET']
redditName = environ['REDDIT_NAME']
redditPass = environ['REDDIT_PASS']
userAgent = environ['REDDIT_USER_AGENT']

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)

filter = bitarray(256)
filter.setall(0)
no_of_hash = 3


def resetFilter():
    logger.info("Resetting Filter...")
    filter.setall(0)


def add(item):
    for i in range(no_of_hash):
        index = mmh3.hash(item, i) % 256
        filter[index] = 1


def find(item):
    for i in range(no_of_hash):
        index = mmh3.hash(item, i) % 256
        if filter[index] == 0:
            return False
    return True


bot = Bot()

reddit = praw.Reddit(
    client_id=clientId,
    client_secret=clientSecret,
    username=redditName,
    password=redditPass,
    user_agent=userAgent,
)


def get_random_subreddit():
    logger.info("Selecting random subreddit...")
    subreddits = [
        "Wallpaper",
        "Wallpapers",
        "BackgroundArt",
        "naturepics",
        "natureporn",
        "EarthPorn"
    ]

    random_subreddit = random.choice(subreddits)
    logger.info("Selected:" + str(random_subreddit))
    return random_subreddit


def remove_file(file):
    time.sleep(5)
    if os.path.exists(file):
        os.remove(file)


def getAffiliateLinks():
    affiliate_text = "\nLive Intentionally: 90 Day Self-Improvement Project - Build Discipline. Fix your habits & " \
                     "routine in 90 days:(https://gumroad.com/a/752219251/vrvFg)" \
                     "\n\nThe Art of Twitter - Start a Twitter based business: " \
                     "Earn $100 per day everyday:(https://gumroad.com/a/752219251/XFFpt)\n"
    return affiliate_text


def upload(fileName, title, type_of):
    logger.info("Inside Insta Upload function...")
    if type_of == 1:
        logger.info("call from reddit")
        newTitle = title + "\n" + getAffiliateLinks() + "\n" + hashtag.get_hashtags()
    else:
        logger.info("call from weekend twitter")
        newTitle = title + "\n" + getAffiliateLinks() + "\n" + hashtag.get_quote_hashtags()

    try:
        bot.login(username=insta_user_name, password=insta_pass)
        bot.upload_photo(fileName, caption=newTitle)
        fileName = fileName + ".REMOVE_ME"
    except Exception as e:
        logger.error("Failed to upload " + str(e))
        return

    remove_file(fileName)


def upload_wallpaper():
    tryCount = 1
    logger.info("Getting subreddit...")
    subreddit = reddit.subreddit(get_random_subreddit())
    logger.info("Getting hot post...")
    topPost = subreddit.hot(limit=5)

    for post in topPost:
        url = post.url
        # logger.info('url is :' + str(url))
        # logger.info("Post_id is " + str(post.id))
        logger.info("Caption is " + str(post.title))

        if tryCount > 3:
            return "Failure, Try-Count Limit Exceeded"

        # print("Try Count : {}".format(tryCount))
        tryCount += 1
        if reddit.submission(post.id).domain != 'i.redd.it':
            logger.info("Post does not have any media")
            continue
        if find(post.id):
            logger.info("Post already added in last 7 days...")
            continue
        else:
            logger.info("Found New Image Post")
            add(post.id)

        file_name = url.split("/")

        if len(file_name) == 0:
            file_name = re.findall("/(.*?)", url)

        file_name = file_name[-1]
        if "." not in file_name:
            file_name += ".jpg"

        if ".png" in file_name:
            logger.info("Image is PNG...")
            continue

        break

    r = requests.get(url)
    with open(file_name, "wb") as f:
        f.write(r.content)

    caption = post.title
    caption = re.sub(r'\(.*\)', '', caption)
    caption = re.sub(r'\[.*\]', '', caption)

    return upload(file_name, caption, 1)
