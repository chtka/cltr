FROM chtka/python-ubuntu

RUN apt-get upgrade -y && apt-get update -y

RUN apt-get install wget -y

RUN mkdir clinical-trials-analysis

ADD . /clinical-trials-analysis

RUN pip3 install -r /clinical-trials-analysis/requirements.txt

RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.21.0/geckodriver-v0.21.0-linux64.tar.gz

RUN tar -xzf geckodriver-v0.21.0-linux64.tar.gz

RUN mv geckodriver /usr/bin/geckodriver

RUN apt-get install -y firefox=59.0.2+build1-0ubuntu1

RUN cd clinical-trials-analysis

CMD cd clinical-trials-analysis && python3 scripts/search_trials.py