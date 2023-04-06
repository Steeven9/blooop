import feedparser as fp

from data import talents

for talent in talents:
    feed = fp.parse(f"https://nitter.net/{talent}/rss")
    for tweet in feed.entries:
        url = tweet.id.split("/")
        if url[3] == talent and "schedule" in tweet.summary.lower():
            print(f"https://twitter.com/{url[3]}/{url[4]}/{url[5][:-2]}")
            print(tweet.summary)
            print()
