# Definitions

- **1 - Basic App** : Basic docker example, it is a image convert app. It converts a rgb image to gray image.
  - **Usage** :
        - `docker build -t {example_image_name}`
        - `docker run -it --rm -v "$(pwd)"/app:/app/ --name {example_container_name} {example_image_name}`
