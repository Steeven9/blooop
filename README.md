# <img src="img/logo.png" width="100"> blooop

[![License](https://img.shields.io/github/license/Steeven9/blooop)](/LICENSE)
[![C/C++ CI](https://github.com/Steeven9/blooop/actions/workflows/docker-image.yml/badge.svg)](https://github.com/Steeven9/blooop/actions/workflows/docker-image.yml)
![Lines](https://img.shields.io/tokei/lines/github/Steeven9/blooop)

RSS feed aggregator for vtubers schedule tweets to
feed our [Hololive](https://holocal.moe) and [Nijisanji](https://nijien.vercel.app) calendars.

## How it works

Blooop obtains the tweets for the specified talents from a Nitter instance,
which then get saved in a MongoDB instance for faster indexing.

Check the [API documentation](https://blooop.moe/docs) to see the available endpoints!

### ⚠️ Warning ⚠️

Blooop's API is still in development, so it can change often and without notice.

Twitter is also changing their API left and right which makes it harder to
get the tweets we need. Expect stuff to break sometimes - check Nitter's
[issues page](https://github.com/zedeus/nitter/issues) for updates.

## Run in Docker

Check and eventually adjust the values in the `docker-compose.yml`
file, then bring up the stack:

    docker-compose up

Browse to `http://localhost:5000` and enjoy!

## Local setup

Assuming you already have a Nitter and MongoDB set up, install the requirements:

    pip install --no-cache-dir -r requirements.txt

Then run the app:

    gunicorn main:app

## Credits

Logo by the one and only [Shiro](https://twitter.com/OgumaShiro)!

This project relies on a self-hosted non-public instance of [Nitter](https://github.com/zedeus/nitter),
an ad- and tracking-free alternative to Twitter - be sure to check it out!

Huge thanks to the teams of `KFP | The Office` and `Nijisanji EN Schedule Team`
for helping with debugging and feature suggestions.
