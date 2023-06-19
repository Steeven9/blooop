import re
from csv import reader
from datetime import datetime
from operator import itemgetter
from os import getenv

import feedparser as fp
from dateutil import parser as dp
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pymongo import ASCENDING, MongoClient

from talents_holo import talents as talents_holo
from talents_niji import talents as talents_niji


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
    id: str
    content: str
    keyword: str
    talent: str
    timestamp: datetime
    url: str
    version: int


# Config
KEYWORDS_SCHEDULE = ["schedule", "weekly", "#PetraOnAir"]
KEYWORDS_GUERILLA = ["guerrilla", "guerilla", "gorilla"]
CONNECTION_STRING = getenv("MONGODB_URI")
API_URL = getenv("TWITTER_API_URL")
CLEANER = re.compile('<.*?>')
TALENTS_LIST: list[Talent] = list(
    filter(lambda x: (x["active"]), talents_holo + talents_niji))
TALENTS_LIST.sort(key=itemgetter("agency", "branch", "generationId", "name"))
SORTING_PARAM = [("id", ASCENDING)]
EXCLUDE_RTS = True
EXCLUDE_REPLIES = True

app = FastAPI(title="blooop")
app.mount("/img", StaticFiles(directory="img"), name="img")


def clean_html(raw_html: str) -> str:
    '''Removes HTML code from a given string'''
    return re.sub(CLEANER, '', raw_html)


def log(msg: str, level="INFO") -> None:
    '''Prints a nicely formatted message to stdout'''
    print(f"[{str(datetime.now())[:-7]}] [{level}] {msg}")


def pull_tweets_from_nitter() -> list[Tweet]:
    tweet_list = []
    num_added = 0
    for talent in TALENTS_LIST:
        query = f"{API_URL}/{talent['account']}/search/rss?f=tweets"
        # exclude RTs and replies
        if EXCLUDE_RTS:
            query += "&e-nativeretweets=on"
        if EXCLUDE_REPLIES:
            query += "&e-replies=on"
        feed = fp.parse(query)
        for tweet in feed.entries:
            url = tweet.id.split("/")
            for keyword in list(KEYWORDS_SCHEDULE + KEYWORDS_GUERILLA):
                tweet_body = tweet.summary.lower()
                keyword = keyword.lower()
                if keyword in tweet_body:
                    has_media = "<img src=" in tweet_body
                    # skip retweets (just to be sure)
                    if EXCLUDE_RTS and url[3] != talent["account"]:
                        continue
                    # normalize keywords
                    if keyword in KEYWORDS_SCHEDULE:
                        keyword = "schedule"
                        # skip schedule tweets with no picture attached
                        if not has_media:
                            continue
                    elif keyword in KEYWORDS_GUERILLA:
                        keyword = "guerilla"
                    tweet_id = url[5][:-2]
                    tweet_url = f"https://twitter.com/{talent['account']}/status/{tweet_id}"
                    item = {
                        "_id": tweet_id,
                        "id": tweet_id,
                        "url": tweet_url,
                        "content": clean_html(tweet.summary),
                        "raw_content": tweet.summary,
                        "has_media": has_media,
                        "talent": talent["account"],
                        "version": 3,
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
    return list(request.app.database["tweets"].find({}).sort(SORTING_PARAM))


@app.get("/tweets/{talent}", summary="Get tweets for a given talent")
def tweets_talent(request: Request, talent: str) -> list[Tweet]:
    return list(request.app.database["tweets"].find({
        "talent": talent
    }).sort(SORTING_PARAM))


@app.get("/tweetsByList/{talents}",
         summary="Get tweets for a comma-separated list of talents")
def tweets_by_list(request: Request, talents: str) -> list[Tweet]:
    talents_list = list(reader([talents]))
    return list(request.app.database["tweets"].find({
        "talent": {
            "$in": talents_list[0]
        }
    }).sort(SORTING_PARAM))


@app.get("/tweetsByServer/{server}",
         summary="Get tweets for a specific fan server")
def tweets_server(request: Request,
                  server: str,
                  newestId: str = None) -> list[Tweet]:
    if server.upper() == "KFP":
        talents = talents_holo
    elif server.upper() == "NEST":
        talents = talents_niji
    else:
        talents = []

    db_filter = {"talent": {"$in": [talent["account"] for talent in talents]}}
    if newestId is not None:
        db_filter["$expr"] = {"$gt": [{"$toLong": "$id"}, int(newestId)]}
    return list(
        request.app.database["tweets"].find(db_filter).sort(SORTING_PARAM))


# UNDOCUMENTED ENDPOINTS - ONLY FOR INTERNAL USE


@app.get("/", include_in_schema=False)
def root():
    return FileResponse('index.html')


@app.get("/health", include_in_schema=False)
def health():
    app.mongodb_client.server_info()
    return "Ok"


@app.get("/populate", include_in_schema=False)
def populate() -> list[Tweet]:
    tweets = pull_tweets_from_nitter()
    return tweets


@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(CONNECTION_STRING,
                                     serverSelectionTimeoutMS=5)
    app.database = app.mongodb_client["schedule"]
    app.mongodb_client.server_info()
    log("Connected to the MongoDB database!")


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()
