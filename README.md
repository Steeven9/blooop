# <img src="img/logo.png" width="100"> blooop

[![License](https://img.shields.io/github/license/Steeven9/blooop)](/LICENSE)
[![C/C++ CI](https://github.com/Steeven9/blooop/actions/workflows/docker-image.yml/badge.svg)](https://github.com/Steeven9/blooop/actions/workflows/docker-image.yml)
![Lines](https://img.shields.io/tokei/lines/github/Steeven9/blooop)

RSS feed aggregator for vtubers schedule tweets to
feed our [Hololive](https://holocal.moe) and [Nijisanji](https://nijien.vercel.app) calendars.

## Warning: API in development, can change often and without notice

## Setup

Clone the repo and install the requirements:

    pip install --no-cache-dir -r requirements.txt

## Usage

    gunicorn main:app

## Run in Docker

Build or pull from [Dockerhub](https://hub.docker.com/repository/docker/steeven9/blooop) the image and run it:

    docker build . -t blooop
    docker run --name blooop -p 5000:5000 blooop

## Credits

Logo by the one and only [Shiro](https://twitter.com/OgumaShiro)!

This project relies on a self-hosted non-public instance of [Nitter](https://github.com/zedeus/nitter),
an ad- and tracking-free alternative to Twitter - be sure to check it out!

Huge thanks to the teams of `KFP | The Office` and `Nijisanji EN Schedule Team`
for helping with debugging and feature suggestions.
