FROM python

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PIP_NO_CACHE_DIR=off

WORKDIR /usr/src/gptbuster

COPY . /usr/src/gptbuster

RUN pip install -r requirements.txt.txt && \
    echo 'gptbuster image was created' && \
    python3 main.py