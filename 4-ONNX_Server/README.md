# ONNX Model Server

High-performance machine learning model serving using ONNX Runtime and FastAPI.

## Features

- ✅ **ONNX Runtime**: Cross-platform, high-performance ML inference
- ✅ **FastAPI**: Modern, fast web framework with automatic API documentation
- ✅ **Python 3.11**: Latest Python with improved performance
- ✅ **UV Package Manager**: Ultra-fast dependency management
- ✅ **Multi-stage Docker Build**: Optimized production images
- ✅ **Type Safety**: Full type annotations with Pydantic models
- ✅ **Health Monitoring**: Built-in health checks and monitoring endpoints
- ✅ **Auto Documentation**: Interactive API docs with Swagger UI

## Quick Start

### Local Development

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Create sample model
uv run python create_model.py

# Run development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Visit http://localhost:8000/docs for interactive API docs
```

### Docker

```bash
# Build the image
docker build -t onnx-model-server .

# Run container
docker run --rm -it \
  -p 8000:8000 \
  --name onnx-server \
  onnx-model-server

# Visit http://localhost:8000/docs for API documentation
```

## API Endpoints

- **GET /** - Health check and service status
- **GET /model/info** - Detailed model information and metadata
- **POST /predict** - Make predictions with input data
- **GET /sample** - Get sample input data for testing
- **POST /reload** - Reload model (useful for model updates)
- **GET /docs** - Interactive API documentation (Swagger UI)
- **GET /redoc** - Alternative API documentation

## Model Format

This server supports ONNX models with the following structure:

```json
{
  "model_name": "random_forest_classifier",
  "model_type": "classification",
  "input_shape": [null, 10],
  "output_classes": 3,
  "features": ["feature_0", "feature_1", ...],
  "class_names": ["class_0", "class_1", "class_2"]
}
```

## Usage Examples

### Health Check
```bash
curl http://localhost:8000/
```

### Model Information
```bash
curl http://localhost:8000/model/info
```

### Make Predictions
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    ]
  }'
```

### Get Sample Data
```bash
curl http://localhost:8000/sample
```

## Python Client Example

```python
import requests
import numpy as np

# Create sample input
data = np.random.randn(5, 10).tolist()

# Make prediction
response = requests.post(
    "http://localhost:8000/predict",
    json={"data": data}
)

result = response.json()
print(f"Predictions: {result['predictions']}")
print(f"Probabilities: {result['probabilities']}")
```

## Adding Your Own Model

1. **Convert your model to ONNX format:**

```python
import onnx
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

# Convert scikit-learn model
initial_type = [('float_input', FloatTensorType([None, n_features]))]
onnx_model = convert_sklearn(model, initial_types=initial_type)

# Save model
with open("models/your_model.onnx", "wb") as f:
    f.write(onnx_model.SerializeToString())
```

2. **Update model path in `app/main.py`:**

```python
MODEL_PATH = Path("models/your_model.onnx")
```

3. **Create metadata file `models/model_metadata.json`:**

```json
{
  "model_name": "your_model",
  "model_type": "classification",
  "input_shape": [null, 10],
  "output_classes": 3,
  "accuracy": 0.95,
  "features": ["feature_0", "feature_1", ...],
  "class_names": ["class_0", "class_1", "class_2"]
}
```

## Performance

- **Cold start**: ~2-3 seconds
- **Inference latency**: ~1-5ms per request
- **Throughput**: ~200-1000 RPS (depending on model complexity)
- **Memory usage**: ~50-200MB (depending on model size)

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

# Start Jupyter for examples
uv run jupyter notebook example_usage.ipynb
```

## Supported Model Types

- **Classification**: Multi-class classification models
- **Regression**: Regression models (with minor modifications)
- **Scikit-learn**: Random Forest, SVM, Logistic Regression, etc.
- **XGBoost**: Gradient boosting models
- **LightGBM**: Light gradient boosting models
- **Custom ONNX**: Any ONNX-compatible model

## Deployment

### Production Docker

```bash
# Multi-stage build for production
docker build --target production -t onnx-server:prod .

# Run with resource limits
docker run --rm -d \
  -p 8000:8000 \
  --memory="512m" \
  --cpus="1.0" \
  --name onnx-server-prod \
  onnx-server:prod
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: onnx-model-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: onnx-model-server
  template:
    metadata:
      labels:
        app: onnx-model-server
    spec:
      containers:
      - name: onnx-server
        image: onnx-model-server:latest
        ports:
        - containerPort: 8000
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
          requests:
            memory: "256Mi"
            cpu: "250m"
        livenessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```