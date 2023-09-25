FROM python:3.11.3-slim-bullseye

RUN apt-get update && apt-get install -y build-essential curl git

RUN mkdir -p /usr/src/csms/backend
RUN mkdir -p /usr/src/csms/frontend

WORKDIR /usr/src/csms

COPY frontend /usr/src/csms/frontend
COPY backend /usr/src/csms/backend

ENV PYTHONPATH=/usr/src/csms/backend
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ARG GITHUB_TOKEN
ENV GITHUB_TOKEN=$GITHUB_TOKEN

RUN pip install git+https://heroyooki:${GITHUB_TOKEN}@github.com/heroyooki/pyocpp_contrib.git
RUN pip install -r backend/requirements.txt --upgrade pip
