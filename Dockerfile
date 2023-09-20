FROM python:alpine

WORKDIR /usr/src/app
EXPOSE 5000
CMD [ "gunicorn", "main:app" ]
HEALTHCHECK CMD [ "curl", "localhost:5000/health" ]

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
