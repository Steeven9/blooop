import re
from datetime import datetime
from os import getenv

import feedparser as fp
import uvicorn
from dateutil import parser as dp
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from pymongo import MongoClient

from data_kfp import talents as talents_kfp
from data_nest import talents as talents_nest

app = FastAPI(title="blooop")
CLEANER = re.compile('<.*?>')
KEYWORDS = ["schedule", "weekly", "guerrilla", "guerilla", "gorilla"]
CONNECTION_STRING = getenv("MONGODB_URI")


def clean_html(raw_html: str):
    return re.sub(CLEANER, '', raw_html)


def log(msg: str, level="INFO") -> None:
    print(f"{str(datetime.now())[:-7]} [{level}] {msg}")


def pull_tweets_from_nitter(talents):
    tweet_list = []
    for talent in talents:
        feed = fp.parse(f"https://nitter.net/{talent}/rss")
        for tweet in feed.entries:
            url = tweet.id.split("/")
            for keyword in KEYWORDS:
                if url[3] == talent and keyword in tweet.summary.lower():
                    tweet_id = url[5][:-2]
                    tweet_url = f"https://twitter.com/{url[3]}/{url[4]}/{tweet_id}"
                    item = {
                        "_id": tweet_id,
                        "url": tweet_url,
                        "content": clean_html(tweet.summary),
                        "talent": talent,
                        "version": 1.0,
                        "keyword": keyword,
                        "timestamp": dp.parse(tweet.published)
                    }
                    app.database["tweets"].update_one(
                        filter={"_id": tweet_id},
                        update={'$setOnInsert': item},
                        upsert=True)
                    tweet_list.append(item)
    # TODO count them correctly
    log(f"Added {len(tweet_list)} tweets to DB")
    return tweet_list


@app.get("/", include_in_schema=False)
def root():
    return FileResponse('index.html')


@app.get("/health", include_in_schema=False)
def health():
    return "Ok"


@app.get("/populate", include_in_schema=False)
def populate():
    tweets = pull_tweets_from_nitter(talents_kfp + talents_nest)
    return tweets


@app.get("/tweets", summary="Get all tweets")
def tweets(request: Request):
    return list(request.app.database["tweets"].find({}))


@app.get("/tweets/{talent}", summary="Get tweets for a given talent")
def tweets_talent(request: Request, talent: str):
    return list(request.app.database["tweets"].find({"talent": talent}))


@app.get("/tweets_kfp", summary="Get tweets for KFP server")
def tweets_kfp(request: Request):
    return list(request.app.database["tweets"].find(
        {"talent": {
            "$in": talents_kfp
        }}))


@app.get("/tweets_nest", summary="Get tweets for NEST server")
def tweets_nest(request: Request):
    return list(request.app.database["tweets"].find(
        {"talent": {
            "$in": talents_nest
        }}))


@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(CONNECTION_STRING)
    app.database = app.mongodb_client["schedule"]
    log("Connected to the MongoDB database!")


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


#TODO add time in logging
if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=5000, host="0.0.0.0")
