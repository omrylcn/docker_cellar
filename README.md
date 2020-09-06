# Definitions

- **1 - Basic App** : Basic docker example, it is a image convert app. It converts a rgb image to a gray image.
  - **Folder** :

    - data/input : input image place
    - data/output : output image place
    - data/param : paramter file place

  - **Usage** :

        - `docker build -t {example_image_name} .`
        - `docker run -it --rm -v "$(pwd)"/app:/app/ --name {example_container_name} {example_image_name}`
