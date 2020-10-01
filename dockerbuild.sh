#!/bin/sh
docker build --build-arg COMMIT=$(git rev-parse HEAD) --build-arg BRANCH=$(git rev-parse --symbolic-full-name HEAD) -t ghcr.io/nh-server/kurisu .
