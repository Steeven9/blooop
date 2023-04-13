from os import getenv

bind = "0.0.0.0:5000"
reload = False if getenv("ENVIRONMENT") == "PROD" else True
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
forwarded_allow_ips = "*"
accesslog = "-"
