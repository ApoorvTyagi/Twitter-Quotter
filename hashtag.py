#import nltk
#from nltk.stem import WordNetLemmatizer

#DEFAULT_CAPTION_PREFIX = "Insta Daily Pic"
#MAX_NUM_HASHTAGS = 11

DEFAULT_HASHTAGS = "#wallpaper #image #picoftheday #art #beautiful #nature #pictures #photos #photography #travelphotography #photooftheday #earth #pod"

def get_hashtags():
    '''
    lemmatizer = WordNetLemmatizer()
    hashtags = list(
        set(
            [
                lemmatizer.lemmatize(word)
                for (word, pos) in nltk.pos_tag(nltk.word_tokenize(text))
                if pos[0] == "N"
            ]
        )
    )  # use nouns to get hashtags
    hashtag_string = (
        "#" + " #".join(hashtags[: min(len(hashtags), (MAX_NUM_HASHTAGS - 8))])
        if len(hashtags) > 0
        else ""
    )  # total upto 19 hashtags (any more and Instagram starts lowering SEO)
    hashtag_string += DEFAULT_HASHTAGS
    #print("Hashtags generated: {}".format(hashtag_string))
    '''
    return DEFAULT_HASHTAGS

def get_quote_hashtags():
    hashtags = "#motivation #quote #inspiration #dailyquotes #wisewords #wordsofwisdom #quoteoftheday #hustle #quotesdaily #qod"
    return hashtags

