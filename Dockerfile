FROM python:3.12-slim

ENV PYTHONUNBUFFERED 1

# RUN apt-get update && apt-get install -y libpq-dev
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
# COPY . /app
