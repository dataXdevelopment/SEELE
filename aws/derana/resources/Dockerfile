FROM python:3.9-alpine

#This dockerfile requires a file, which is the main executable to be passed in
ARG FILE_NAME

WORKDIR /app

COPY requirements.txt  .

RUN  pip3 install -r requirements.txt 

COPY ${FILE_NAME} index.py
