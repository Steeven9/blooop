import re
from datetime import datetime
from operator import itemgetter
from os import getenv

import feedparser as fp
from dateutil import parser as dp
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pymongo import MongoClient

from data_kfp import talents as talents_kfp
from data_nest import talents as talents_nest


class Talent(BaseModel):
    account: str
    name: str
    agency: str
    branch: str
    generation: str
    generationId: int
    active: bool
    colors: dict


class Tweet(BaseModel):
    _id: str
    content: str
    keyword: str
    talent: str
    timestamp: datetime
    url: str
    version: int


# Config
KEYWORDS = ["schedule", "weekly", "guerrilla", "guerilla", "gorilla"]
CONNECTION_STRING = getenv("MONGODB_URI")
API_URL = getenv("TWITTER_API_URL")
CLEANER = re.compile('<.*?>')
TALENTS_LIST: list[Talent] = list(
    filter(lambda x: (x["active"]), talents_kfp + talents_nest))
TALENTS_LIST.sort(key=itemgetter("agency", "branch", "generationId", "name"))

app = FastAPI(title="blooop")
app.mount("/img", StaticFiles(directory="img"), name="img")


def clean_html(raw_html: str) -> str:
    return re.sub(CLEANER, '', raw_html)


def log(msg: str, level="INFO") -> None:
    print(f"[{str(datetime.now())[:-7]}] [{level}] {msg}")


def pull_tweets_from_nitter() -> list[Tweet]:
    tweet_list = []
    num_added = 0
    for talent in TALENTS_LIST:
        feed = fp.parse(f"{API_URL}/{talent['account']}/rss")
        for tweet in feed.entries:
            url = tweet.id.split("/")
            for keyword in KEYWORDS:
                if url[3] == talent[
                        "account"] and keyword in tweet.summary.lower():
                    tweet_id = url[5][:-2]
                    tweet_url = f"https://twitter.com/{talent['account']}/status/{tweet_id}"
                    item = {
                        "_id": tweet_id,
                        "url": tweet_url,
                        "content": clean_html(tweet.summary),
                        "talent": talent["account"],
                        "version": 1.0,
                        "keyword": keyword,
                        "timestamp": dp.parse(tweet.published)
                    }
                    res = app.database["tweets"].update_one(
                        filter={"_id": tweet_id},
                        update={'$setOnInsert': item},
                        upsert=True)
                    num_added = num_added + res.modified_count
                    tweet_list.append(item)
    log(f"Added {num_added} tweets to DB (fetched {len(tweet_list)})")
    return tweet_list


@app.get("/talents", summary="List all watched talents")
def talents() -> list[Talent]:
    return TALENTS_LIST


@app.get("/tweets", summary="Get all tweets")
def tweets(request: Request) -> list[Tweet]:
    return list(request.app.database["tweets"].find({}))


@app.get("/tweets/{talent}", summary="Get tweets for a given talent")
def tweets_talent(request: Request, talent: str) -> list[Tweet]:
    return list(request.app.database["tweets"].find({"talent": talent}))


#TODO tweets endpoint but with a list param


@app.get("/tweets_kfp", summary="Get tweets for KFP server")
def tweets_kfp(request: Request) -> list[Tweet]:
    return list(request.app.database["tweets"].find(
        {"talent": {
            "$in": talents_kfp
        }}))


@app.get("/tweets_nest", summary="Get tweets for NEST server")
def tweets_nest(request: Request) -> list[Tweet]:
    return list(request.app.database["tweets"].find(
        {"talent": {
            "$in": talents_nest
        }}))


# UNDOCUMENTED ENDPOINTS - ONLY FOR INTERNAL USE


@app.get("/", include_in_schema=False)
def root():
    return FileResponse('index.html')


@app.get("/health", include_in_schema=False)
def health():
    return "Ok"


@app.get("/populate", include_in_schema=False)
def populate() -> list[Tweet]:
    tweets = pull_tweets_from_nitter()
    return tweets


@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(CONNECTION_STRING)
    app.database = app.mongodb_client["schedule"]
    log("Connected to the MongoDB database!")


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()
