FROM ubuntu:latest

RUN mkdir clinical-trials-analysis

ADD . /clinical-trials-analysis

RUN apt-get upgrade && apt-get update -y

RUN apt-get install wget -y

RUN apt-get install python3 -y && apt-get install python3-pip -y

RUN pip3 install -r /clinical-trials-analysis/requirements.txt

RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.21.0/geckodriver-v0.21.0-linux64.tar.gz

RUN tar -xzf geckodriver-v0.21.0-linux64.tar.gz

RUN mv geckodriver /usr/bin/geckodriver