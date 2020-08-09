import praw, requests, re
import os
import random
import time
import logging
import mmh3
from bitarray import bitarray
from instabot import Bot
from os import environ
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

filter=bitarray(256) 
filter.setall(0)
no_of_hash=3 

def resetFilter():
    logger.info("Reseting Filter...")
    filter.setall(0)

def add(item):
    for i in range(no_of_hash):
        index=mmh3.hash(item,i)%256
        filter[index]=1

def find(item):
    for i in range(no_of_hash):
        index=mmh3.hash(item,i)%256
        if filter[index]==0:
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
    logger.info("Selceting random subreddit...")
    #subreddits = ["Wallpapers"]
    subreddits = [
        "Wallpaper",
        "Wallpapers",
        "BackgroundArt",
        "naturepics",
        "natureporn",
        "EarthPorn"
    ]

    random_subreddit = random.choice(subreddits)
    logger.info("Selected:"+str(random_subreddit))
    return random_subreddit

def remove_file(File):
    time.sleep(2)
    os.remove(File)

def upload(fileName,title):
    newTitle=title+"\n"+hashtag.get_hashtags(title)
    logger.info("Inside Insta Upload function...")
    try:
        bot.login(username = insta_user_name, password = insta_pass)
        bot.upload_photo(fileName, caption = newTitle)
        fileName=fileName+".REMOVE_ME"
    except Exception as e:
        logger.error("Failed to upload " + str(e))
        return

    remove_file(fileName)


def upload_wallpaper():
    tryCount=1
    logger.info("Getting subreddit...")
    subreddit = reddit.subreddit(get_random_subreddit())
    logger.info("Getting hot post...")
    topPost = subreddit.hot(limit=5)

    for post in topPost:
        url = post.url
        #logger.info('url is :' + str(url))
        #logger.info("Post_id is " + str(post.id))
        logger.info("Caption is " + str(post.title))
        
        if tryCount>3:
            return "Failure, Try-Count Limit Exceeded"

        
        #print("Try Count : {}".format(tryCount))
        tryCount+=1
        if(reddit.submission(post.id).domain != 'i.redd.it'):
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

        break

    r = requests.get(url)
    with open(file_name, "wb") as f:
        f.write(r.content)

    caption=post.title    
    caption = re.sub(r'\(.*\)', '', caption)
    caption = re.sub(r'\[.*\]', '', caption)

    
    return upload(file_name,caption)
