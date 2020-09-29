#!/bin/sh
docker build --build-arg COMMIT=$(git rev-parse HEAD) --build-arg BRANCH=$(git rev-parse --abbrev-ref HEAD) -t ghcr.io/nh-server/kurisu .
