# `Docker Commands`

## `Basic Docker Commands`

### RUN - START A CONTAINER

- docker run ubuntu
- docker run -it ubuntu 

### PS-LIST CONTAINERS

- docker ps  
- docker ps -a

### START-STOP_CONTAINNERS

- docker stop container_name
- docker start container_name

### REMOVE A CONTAINER

- docker rm container_name

### IMAGES-LIST IMAGES

- docker images

### REMOVE DOCKER IMAGES

- docker rmi docker-image

### PULL - DOWNLOAD IMAGES

- docker pull docker-image

### APPEND A COMMAND

- docker run ubuntu sleep 1000
- docker run -d ubuntu sleep 20 # run backround and 20 seconds

## `Docker Run Commands`

### RUN-TAG

- docker run Ubuntu:17.04

### RUN-ATTACH AND DETACH

- docker run -d docker_container
- docker attach docker_container

### RUN-STDIN

- docker run -i docker_container # statndard input of your docker host

### PORT MAPPING

- docker run -p 80:5000 docker_container

### VOLUME MAPPING

- docker run -V /new_dir/:/var/lib/docker_container  container

## `Docker All Containers`

### REMOVE ALL CONTAINERS

- docker rm $(docker ps -a -q)

