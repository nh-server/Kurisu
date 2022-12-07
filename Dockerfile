FROM python:3.9-alpine

ENV IS_DOCKER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

ENV HOME /home/kurisu
RUN addgroup -g 2849 kurisu && adduser -u 2849 -h $HOME -D -G kurisu kurisu
WORKDIR $HOME
COPY ./requirements.txt .
RUN set -eux \
	&& apk add --no-cache libpq libjpeg-turbo \
	&& pip install --no-compile --no-cache-dir -r requirements.txt
USER kurisu

#COPY data data
RUN mkdir data
COPY kurisu.py kurisu.py
COPY utils utils
COPY cogs cogs

ARG BRANCH="unknown"
ENV COMMIT_BRANCH=${BRANCH}
ARG COMMIT="unknown"
ENV COMMIT_SHA=${COMMIT}

LABEL org.opencontainers.image.title Kurisu
LABEL org.opencontainers.image.description Discord moderation bot for Nintendo Homebrew
LABEL org.opencontainers.image.source https://github.com/nh-server/Kurisu
LABEL org.opencontainers.image.url https://github.com/nh-server/Kurisu
LABEL org.opencontainers.image.licenses Apache-2.0
LABEL org.opencontainers.image.revision $COMMIT

CMD ["python3", "kurisu.py"]
