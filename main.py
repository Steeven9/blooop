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

from keywords import KEYWORDS_GUERILLA, KEYWORDS_SCHEDULE
from talents_holo import talents as talents_holo
from talents_niji import talents as talents_niji


class Talent(BaseModel):
    account: str
    name: str
    agency: str
    generation: str
    generationId: int
    active: bool
    colors: dict


class Tweet(BaseModel):
    id: str
    content: str
    keyword: str
    talent: str
    published: datetime
    url: str
    version: int


# Config
CONNECTION_STRING = getenv("MONGODB_URI")
API_URL = getenv("TWITTER_API_URL")
CLEANER = re.compile('<.*?>')
ACTIVE_TALENTS_LIST: list[Talent] = list(
    filter(lambda x: (x["active"]), talents_holo + talents_niji))
ACTIVE_TALENTS_HOLO: list[Talent] = list(
    filter(lambda x: (x["active"]), talents_holo))
ACTIVE_TALENTS_NIJI: list[Talent] = list(
    filter(lambda x: (x["active"]), talents_niji))
SORTING_PARAM = [("id", ASCENDING)]
EXCLUDE_RTS = True
EXCLUDE_REPLIES = True

ACTIVE_TALENTS_LIST.sort(key=itemgetter("agency", "generationId", "name"))
ACTIVE_TALENTS_HOLO.sort(key=itemgetter("agency", "generationId", "name"))
ACTIVE_TALENTS_NIJI.sort(key=itemgetter("generationId", "name"))

if CONNECTION_STRING == None:
    raise ValueError("Missing connection string!")
if API_URL == None:
    raise ValueError("Missing API URL!")

app = FastAPI(title="blooop")
app.mount("/img", StaticFiles(directory="img"), name="img")


def clean_html(raw_html: str) -> str:
    '''Removes HTML code from a given string'''
    return re.sub(CLEANER, '', raw_html)


def log(msg: str, level="INFO") -> None:
    '''Prints a nicely formatted message to stdout'''
    print(f"[{str(datetime.now())[:-7]}] [{level}] {msg}")


# https://github.com/zedeus/nitter
def pull_tweets_from_nitter() -> list[Tweet]:
    tweet_list = []
    num_added = 0
    for talent in ACTIVE_TALENTS_LIST:
        query = f"{API_URL}/search/rss?f=tweets&q=from%3A{talent['account']}"
        # exclude RTs and replies
        if EXCLUDE_RTS:
            query += "&e-nativeretweets=on&e-quote=on"
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
                    else:
                        keyword = "other"
                    tweet_id = url[5][:-2]
                    tweet_url = f"https://twitter.com/{talent['account']}/status/{tweet_id}"
                    now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                    item = {
                        "_id": tweet_id,
                        "id": tweet_id,
                        "url": tweet_url,
                        "content": clean_html(tweet.summary),
                        "raw_content": tweet.summary,
                        "has_media": has_media,
                        "talent": talent["account"].lower(),
                        "version": 4,
                        "source": "nitter",
                        "keyword": keyword,
                        "published": dp.parse(tweet.published),
                        "scraped": dp.parse(now)
                    }
                    res = app.database["tweets"].update_one(
                        filter={"_id": tweet_id},
                        update={'$setOnInsert': item},
                        upsert=True)
                    num_added = num_added + res.modified_count
                    tweet_list.append(item)
                    break
    log(f"Added {num_added} tweets to DB (fetched {len(tweet_list)})")
    return tweet_list


# https://github.com/12joan/twitter-client
def pull_tweets_from_twitter_client() -> list[Tweet]:
    tweet_list = []
    num_added = 0
    for talent in ACTIVE_TALENTS_LIST:
        query = f"{API_URL}/{talent['account']}/rss"
        feed = fp.parse(query)
        for tweet in feed.entries:
            url = tweet.link.split("/")
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
                    else:
                        keyword = "other"
                    tweet_id = url[5]
                    tweet_url = f"https://twitter.com/{talent['account']}/status/{tweet_id}"
                    now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                    item = {
                        "_id": tweet_id,
                        "id": tweet_id,
                        "url": tweet_url,
                        "content": clean_html(tweet.summary),
                        "raw_content": tweet.summary,
                        "has_media": has_media,
                        "talent": talent["account"].lower(),
                        "version": 4,
                        "source": "twitter-client",
                        "keyword": keyword,
                        "published": dp.parse(tweet.published),
                        "scraped": dp.parse(now)
                    }
                    res = app.database["tweets"].update_one(
                        filter={"_id": tweet_id},
                        update={'$setOnInsert': item},
                        upsert=True)
                    num_added = num_added + res.modified_count
                    tweet_list.append(item)
                    break
    log(f"Added {num_added} tweets to DB (fetched {len(tweet_list)})")
    return tweet_list


@app.get("/talents", summary="List all watched talents")
def talents() -> list[Talent]:
    return ACTIVE_TALENTS_LIST


@app.get("/talents/{server}", summary="List watched talents for a server")
def talents(server: str) -> list[Talent]:
    if server.upper() == "KFP":
        return ACTIVE_TALENTS_HOLO
    elif server.upper() == "NEST":
        return ACTIVE_TALENTS_NIJI
    else:
        return []


@app.get("/tweets", summary="Get all tweets")
def tweets(request: Request) -> list[Tweet]:
    return list(request.app.database["tweets"].find({}).sort(SORTING_PARAM))


@app.get("/tweets/{talent}", summary="Get tweets for a given talent")
def tweets_talent(request: Request, talent: str) -> list[Tweet]:
    return list(request.app.database["tweets"].find({
        "talent": talent.lower()
    }).sort(SORTING_PARAM))


@app.get("/tweetsByList/{talents}",
         summary="Get tweets for a comma-separated list of talents")
def tweets_by_list(request: Request, talents: str) -> list[Tweet]:
    talents_list = list(reader([talent.lower() for talent in talents]))
    return list(request.app.database["tweets"].find({
        "talent": {
            "$in": talents_list[0]
        }
    }).sort(SORTING_PARAM))


@app.get("/tweetsByServer/{server}",
         summary="Get tweets for a specific fan server")
def tweets_server(
    request: Request,
    server: str,
    # DO NOT RENAME THIS VARIABLE TO PLEASE SONARLINT!!!!!! IT WILL BREAK THE API!!!!
    newestId: str = None
) -> list[Tweet]:
    if server.upper() == "KFP":
        talents = ACTIVE_TALENTS_HOLO
    elif server.upper() == "NEST":
        talents = ACTIVE_TALENTS_NIJI
    else:
        talents = []

    db_filter = {
        "talent": {
            "$in": [talent["account"].lower() for talent in talents]
        }
    }
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
                                     serverSelectionTimeoutMS=5,
                                     appname="blooop")
    app.database = app.mongodb_client["schedule"]
    app.mongodb_client.server_info()
    log("Connected to the MongoDB database!")


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()
