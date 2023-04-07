import re

import feedparser as fp
import uvicorn
from fastapi import FastAPI

from data_kfp import talents as talents_kfp
from data_nest import talents as talents_nest

app = FastAPI()
CLEANER = re.compile('<.*?>')


def clean_html(raw_html):
    return re.sub(CLEANER, '', raw_html)


def get_tweets(talents):
    tweet_list = []
    for talent in talents:
        feed = fp.parse(f"https://nitter.net/{talent}/rss")
        for tweet in feed.entries:
            url = tweet.id.split("/")
            if url[3] == talent and "schedule" in tweet.summary.lower():
                tweet_url = f"https://twitter.com/{url[3]}/{url[4]}/{url[5][:-2]}"
                tweet_list.append({
                    "url": tweet_url,
                    "tweet": clean_html(tweet.summary),
                    "talent": talent
                })
    return tweet_list


@app.get("/")
def root():
    return "Hello! Check out /docs to see the available endpoints"


@app.get("/health")
def root():
    return "Ok"


@app.get("/tweets_kfp")
def tweets_kfp():
    tweets = get_tweets(talents_kfp)
    return {"tweets": tweets, "talents": talents_kfp}


@app.get("/tweets_nest")
def tweets_nest():
    tweets = get_tweets(talents_nest)
    return {"tweets": tweets, "talents": talents_nest}


@app.get("/tweets/{talent}")
def tweets_talent(talent: str):
    tweets = get_tweets([talent])
    return {"tweets": tweets, "talent": talent}


if __name__ == "__main__":
    uvicorn.run("main:app",
                reload=True,
                port=5000,
                log_level="info",
                host="0.0.0.0")
