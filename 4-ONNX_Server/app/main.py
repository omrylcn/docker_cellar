"""ONNX Runtime model serving with FastAPI."""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

import numpy as np
import onnxruntime as ort
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ONNX Model Server",
    description="High-performance ONNX model serving with FastAPI",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and metadata
MODEL_SESSION: Optional[ort.InferenceSession] = None
MODEL_METADATA: Dict[str, Any] = {}
MODEL_PATH = Path("models/random_forest_classifier.onnx")
METADATA_PATH = Path("models/model_metadata.json")


class PredictionRequest(BaseModel):
    """Request model for predictions."""
    
    data: List[List[float]] = Field(
        ..., 
        description="Input data as list of feature vectors",
        example=[[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]]
    )


class PredictionResponse(BaseModel):
    """Response model for predictions."""
    
    predictions: List[int] = Field(..., description="Predicted class labels")
    probabilities: List[List[float]] = Field(..., description="Class probabilities")
    model_info: Dict[str, Any] = Field(..., description="Model metadata")


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Model loading status")
    model_name: str = Field(..., description="Loaded model name")
    version: str = Field(..., description="Service version")


def load_model() -> None:
    """Load ONNX model and metadata."""
    global MODEL_SESSION, MODEL_METADATA
    
    try:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
        
        # Load ONNX model
        MODEL_SESSION = ort.InferenceSession(
            str(MODEL_PATH),
            providers=['CPUExecutionProvider']
        )
        
        # Load metadata
        if METADATA_PATH.exists():
            with open(METADATA_PATH, 'r') as f:
                MODEL_METADATA = json.load(f)
        else:
            MODEL_METADATA = {"model_name": "unknown", "model_type": "unknown"}
        
        logger.info(f"✅ Model loaded successfully: {MODEL_METADATA.get('model_name', 'unknown')}")
        
    except Exception as e:
        logger.error(f"❌ Failed to load model: {str(e)}")
        raise


@app.on_event("startup")
async def startup_event():
    """Load model on startup."""
    load_model()


@app.get("/", response_model=HealthResponse, summary="Health check")
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if MODEL_SESSION is not None else "unhealthy",
        model_loaded=MODEL_SESSION is not None,
        model_name=MODEL_METADATA.get("model_name", "unknown"),
        version="0.1.0"
    )


@app.get("/model/info", summary="Get model information")
async def get_model_info() -> Dict[str, Any]:
    """Get detailed model information."""
    if MODEL_SESSION is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    # Get ONNX model info
    model_inputs = [
        {
            "name": input_meta.name,
            "type": str(input_meta.type),
            "shape": input_meta.shape
        }
        for input_meta in MODEL_SESSION.get_inputs()
    ]
    
    model_outputs = [
        {
            "name": output_meta.name,
            "type": str(output_meta.type),
            "shape": output_meta.shape
        }
        for output_meta in MODEL_SESSION.get_outputs()
    ]
    
    return {
        **MODEL_METADATA,
        "onnx_inputs": model_inputs,
        "onnx_outputs": model_outputs,
        "providers": MODEL_SESSION.get_providers()
    }


@app.post("/predict", response_model=PredictionResponse, summary="Make predictions")
async def predict(request: PredictionRequest) -> PredictionResponse:
    """Make predictions using the loaded ONNX model."""
    if MODEL_SESSION is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    try:
        # Convert input to numpy array
        input_data = np.array(request.data, dtype=np.float32)
        
        # Validate input shape
        expected_features = MODEL_METADATA.get("input_shape", [None, None])[1]
        if expected_features and input_data.shape[1] != expected_features:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input shape. Expected {expected_features} features, got {input_data.shape[1]}"
            )
        
        # Get model input name
        input_name = MODEL_SESSION.get_inputs()[0].name
        
        # Run inference
        outputs = MODEL_SESSION.run(None, {input_name: input_data})
        
        # Extract predictions and probabilities
        predictions = outputs[0].tolist()
        probabilities = outputs[1].tolist() if len(outputs) > 1 else []
        
        return PredictionResponse(
            predictions=predictions,
            probabilities=probabilities,
            model_info={
                "model_name": MODEL_METADATA.get("model_name", "unknown"),
                "model_type": MODEL_METADATA.get("model_type", "unknown"),
                "input_shape": input_data.shape
            }
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@app.get("/sample", summary="Get sample input data")
async def get_sample_data() -> Dict[str, Any]:
    """Get sample input data for testing."""
    sample_path = Path("models/sample_data.json")
    
    if not sample_path.exists():
        return {
            "message": "No sample data available",
            "sample_input": [[1.0] * MODEL_METADATA.get("input_shape", [None, 10])[1]]
        }
    
    try:
        with open(sample_path, 'r') as f:
            sample_data = json.load(f)
        return sample_data
    except Exception as e:
        logger.error(f"Error loading sample data: {str(e)}")
        return {"error": "Failed to load sample data"}


@app.post("/reload", summary="Reload model")
async def reload_model() -> Dict[str, str]:
    """Reload the ONNX model (useful for model updates)."""
    try:
        load_model()
        return {
            "message": "Model reloaded successfully",
            "model_name": MODEL_METADATA.get("model_name", "unknown")
        }
    except Exception as e:
        logger.error(f"Model reload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model reload failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )