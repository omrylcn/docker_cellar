# FastAPI Image Processing Service

Modern FastAPI service for image processing with automatic OpenAPI documentation and async support.

## Features

- ✅ **FastAPI**: Modern, fast web framework with automatic API documentation
- ✅ **Python 3.11**: Latest Python with improved performance
- ✅ **UV Package Manager**: Ultra-fast Python package management
- ✅ **Multi-stage Docker Build**: Optimized production images
- ✅ **Type Hints**: Full type annotation support
- ✅ **CORS Support**: Cross-origin requests enabled
- ✅ **File Upload**: Async file upload with validation
- ✅ **Health Checks**: Built-in health monitoring

## API Endpoints

- **GET /** - Health check endpoint
- **GET /inputs** - List uploaded files
- **GET /outputs** - List converted files
- **GET /download/{filename}** - Download converted file
- **POST /upload** - Upload image file for processing
- **POST /convert** - Convert uploaded images to grayscale
- **GET /docs** - Interactive API documentation (Swagger UI)
- **GET /redoc** - Alternative API documentation

## Usage

### Local Development

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run development server with auto-reload
uv run uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Visit http://localhost:8000/docs for interactive API docs
```

### Docker

```bash
# Build the image
docker build -t fastapi-image-processor .

# Run container
docker run --rm -it \
  -p 8000:8000 \
  -v "$(pwd)/app/project:/app/project" \
  --name image-api \
  fastapi-image-processor

# Visit http://localhost:8000/docs for API documentation
```

## API Usage Examples

### Upload an image
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@your_image.jpg"
```

### Convert uploaded images
```bash
curl -X POST "http://localhost:8000/convert"
```

### List converted files
```bash
curl "http://localhost:8000/outputs"
```

### Download converted file
```bash
curl -O "http://localhost:8000/download/your_image_grayscale.jpg"
```

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff)
- WebP (.webp)

## Development

```bash
# Install dev dependencies
uv sync --extra dev

# Format code
uv run black app/
uv run ruff check app/

# Type checking
uv run mypy app/

# Run tests
uv run pytest
```

## Environment Variables

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `WORKERS`: Number of worker processes (default: 1)
- `LOG_LEVEL`: Logging level (default: info)