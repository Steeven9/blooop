# <img src="logo.png" width="100"> ScheduleYoinker

[![License](https://img.shields.io/github/license/Steeven9/ScheduleYoinker)](/LICENSE)
[![C/C++ CI](https://github.com/Steeven9/ScheduleYoinker/actions/workflows/docker-image.yml/badge.svg)](https://github.com/Steeven9/ScheduleYoinker/actions/workflows/docker-image.yml)
![Lines](https://img.shields.io/tokei/lines/github/Steeven9/ScheduleYoinker)

RSS feed aggregator for vtubers schedule tweets to
feed our [Hololive](https://holocal.moe) and [Nijisanji](https://nijien.vercel.app) calendars.

## Setup

Clone the repo and install the requirements:

    pip install --no-cache-dir -r requirements.txt

## Usage

    python main.py

## Run in Docker

Build or pull the image and run it:

    docker build . -t scheduleyoinker
    docker run --name scheduleyoinker -p 5000:5000 scheduleyoinker

## Credits

Profile picture by the one and only [DuDuL](https://twitter.com/DuDuLtv)!

This project uses [Nitter](https://nitter.net), an alternative to Twitter - be sure to check it out!

Huge thanks to the team at `KFP | The Office` for helping with debugging
and feature suggestions.
