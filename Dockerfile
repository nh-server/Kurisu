FROM python:3.8.5-slim-buster
LABEL org.opencontainers.image.source https://github.com/nh-server/Kurisu
ENV HOME /home/kurisu
RUN useradd -m -d $HOME -s /bin/sh -u 2849 kurisu
WORKDIR $HOME
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENV IS_DOCKER=1
ARG COMMIT="unknown"
ARG BRANCH="unknown"
ENV COMMIT_SHA=${COMMIT}
ENV COMMIT_BRANCH=${BRANCH}
USER kurisu
COPY --chown=2849:2849 . .
CMD ["python3", "kurisu.py"]
