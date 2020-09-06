# Docker Guide

**List all docker images**
- `docker images -a`

**Remove all docker images**
- `docker rmi $(docker images -a -q)`

**List all docker containers**
- `docker ps -a -f status=exited`

**Remove all docker containers**
- `docker ps -a | grep "pattern" | awk '{print $1}' | xargs docker rm`

**Build docker images**
- `docker build -t test-image`

**Run docker images with some parameters like volume**
- docker run -it --rm -v "$(pwd)"/app:/app/ --name test test-ski

