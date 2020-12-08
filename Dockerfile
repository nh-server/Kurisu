FROM python:3.8-slim
LABEL org.opencontainers.image.source https://github.com/nh-server/Kurisu
ENV IS_DOCKER=1
ENV PYTHONUNBUFFERED=1
ENV HOME /home/kurisu
RUN useradd -m -d $HOME -s /bin/sh -u 2849 kurisu
WORKDIR $HOME
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
USER kurisu
ARG BRANCH="unknown"
ENV COMMIT_BRANCH=${BRANCH}
ARG COMMIT="unknown"
ENV COMMIT_SHA=${COMMIT}
COPY --chown=2849:2849 . .
CMD ["python3", "kurisu.py"]
