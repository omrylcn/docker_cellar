
- `docker build -t {example_image_name} .`
- `docker run --rm -it -v "$(pwd)"/app:/app --name test -p 5000:5000 {example_image_name}`