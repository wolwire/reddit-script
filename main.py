import http.client
import mimetypes
import json
import praw
import yaml
import time
import nltk
import logging
import logging.config

logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def load_settings():
    with open(r'/Users/mayank/reddit-praw-bot/settings.local.yaml') as file:
        global settings
        global sentiment_analyzer
        global trigger_phrases
        settings = yaml.load(file, Loader=yaml.FullLoader)
        sentiment_analyzer = SentimentIntensityAnalyzer()
        trigger_phrases = settings["bot"]["trigger_phrases"]
        return settings


def find_sentiment_scores(sentence):
    scores = sentiment_analyzer.polarity_scores(sentence)
    return scores


def load_reddit_instance():
    credentials = settings['credentials']
    client_id = credentials['client_id']
    client_secret = credentials['client_secret']
    username = credentials['username']
    password = credentials['password']
    user_agent = credentials['user_agent']

    reddit = praw.Reddit(client_id=client_id,
                         client_secret=client_secret,
                         username=username,
                         password=password,
                         user_agent=user_agent)

    return reddit


def run_bot(reddit_instance, subreddit):
    subreddit_instance = reddit_instance.subreddit(subreddit)
    for comment in subreddit_instance.stream.comments():
        comment_text = comment.body
        # check if comment is not Null and in correct subreddits and the bot doesn't gets involved in recursion
        if comment_text is not None and comment.subreddit not in settings['subs']['blacklist'] and comment.subreddit in settings['subs']['whitelist'] and comment_text != settings["bot"]["reply_text"]:
           # if triggers are hit start actions and comment
            for x in trigger_phrases:
                if x in comment_text:
                    #find sentiment scores
                    scores = find_sentiment_scores(comment_text)
                    if scores['compound'] < 0:
                        reply = settings["bot"]["reply_text"]
                        reply = reply + f"\npositive|negative|neutral\n-|-|-\n{scores['pos']}|{scores['neg']}|{scores['neu']}"
                        try:
                            comment.reply(reply)
                            time.sleep(1000)
                            break
                        except Exception as e:
                            print(e)
                            time.sleep(100)
                            break


if __name__ == '__main__':
    load_settings()
    reddit = load_reddit_instance()
    # start bot (bot go brrrrrrrrrrrr)
    while True:
        run_bot(reddit, 'all')

