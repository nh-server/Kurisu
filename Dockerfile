FROM python:3.9

ENV IS_DOCKER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV HOME /home/kurisu
RUN useradd -m -d $HOME -s /bin/sh -u 2849 kurisu
WORKDIR $HOME
COPY ./requirements.txt .
RUN pip install --no-compile --no-cache-dir -r requirements.txt
USER kurisu
COPY . .

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
