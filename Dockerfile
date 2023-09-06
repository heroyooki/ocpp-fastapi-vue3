FROM python:3.11.3-slim-bullseye

RUN apt-get update && apt-get install -y build-essential curl

RUN mkdir -p /usr/src/csms/backend
RUN mkdir -p /usr/src/csms/frontend

WORKDIR /usr/src/csms

COPY backend/src /usr/src/csms/backend
COPY frontend /usr/src/csms/frontend

ENV PYTHONPATH=/usr/src/csms/backend
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --no-cache-dir -r /usr/src/csms/backend/requirements.txt --upgrade pip

