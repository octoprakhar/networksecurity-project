# FROM python:3.10-slim-buster
# WORKDIR /app
# COPY . /app

# RUN apt update -y && apt install awscli -y

# RUN apt-get update && pip install -r requirements.txt

# CMD [ "python3","app.py" ]

FROM python:3.10-slim-bookworm

WORKDIR /app
COPY . /app

RUN apt-get update -y && apt-get install -y awscli

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python3", "app.py" ]