# Basic Image Converter

Modern Python 3.11 application for converting RGB images to grayscale using scikit-image.

## Features

- ✅ Python 3.11 with type hints
- ✅ UV package manager for fast dependency resolution
- ✅ Multi-stage Docker build for optimized images
- ✅ Proper error handling and logging
- ✅ Code quality tools (ruff, black, mypy)

## Usage

### Local Development

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run the application
uv run python app/run.py
```

### Docker

```bash
# Build the image
docker build -t basic-image-converter .

# Run with volume mount
docker run -it --rm \
  -v "$(pwd)/app:/app" \
  --name image-converter \
  basic-image-converter
```

## Configuration

Place your parameters in `app/data/param/parameters.json`:

```json
{
  "input_directory": "data/input/test_image.jpg",
  "output_directory": "data/output/test_image_gray.jpg"
}
```

## Development

```bash
# Install dev dependencies
uv sync --extra dev

# Format code
uv run black app/
uv run ruff check app/

# Type checking
uv run mypy app/
```