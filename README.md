# <img src="logo.png" width="100"> ScheduleYoinker

[![License](https://img.shields.io/github/license/Steeven9/ScheduleYoinker)](/LICENSE)
[![C/C++ CI](https://github.com/Steeven9/ScheduleYoinker/actions/workflows/docker-image.yml/badge.svg)](https://github.com/Steeven9/ScheduleYoinker/actions/workflows/docker-image.yml)
![Lines](https://img.shields.io/tokei/lines/github/Steeven9/ScheduleYoinker)

RSS feed aggregator for vtubers schedule tweets to
feed our [Hololive](https://holocal.moe) and [Nijisanji](https://nijien.vercel.app) calendars.

## Setup

1. Obtain a [Twitter API Bearer token](https://developer.twitter.com/en/docs/twitter-api) and
a [Discord bot token](https://www.writebots.com/discord-bot-token).

2. Create a Twitter List with all the talents you want to monitor and save its id.

3. Clone the repo and install the requirements:

    `pip install --no-cache-dir -r requirements.txt`

4. Set the following environment variables with the two respective values:

    ```bash
    TWITTER_BEARER_TOKEN
    NAMEBOT_TOKEN
    ```

    Note: `NAME` is the alias you want to set for the bot (must match `bot_name` in `data.py`).

5. Customize the configuration for scraping and notifying: edit the `data.py` file and fill in all the values.

6. Finally, run `python main.py`. If everything went well, you should see an output similar to this:

    ```bash
    2023-02-18 00:26:56 [NAME] Loaded 27 talents and 2 extra pings
    2023-02-18 00:26:56 [NAME] Logged in as <your bot name and ID>
    ```

## Usage

TBD

## Run in Docker

Create a `.env` file with the environment variables mentioned in step 4,
then build or pull the image and run it:

`docker build . -t scheduleyoinker`

`docker run --name scheduleyoinker --env-file .env scheduleyoinker`

## Credits

Profile picture by the one and only [DuDuL](https://twitter.com/DuDuLtv)!

Huge thanks to the team at `KFP | The Office` for helping with debugging
and feature suggestions.
