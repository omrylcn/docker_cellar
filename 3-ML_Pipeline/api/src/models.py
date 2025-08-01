"""Pydantic models for ML Pipeline API."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """Request model for predictions."""
    
    data: List[List[float]] = Field(
        ...,
        description="Input data as list of feature vectors",
        example=[[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]]
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use Redis caching for this prediction"
    )
    cache_ttl: int = Field(
        default=3600,
        description="Cache TTL in seconds",
        ge=1,
        le=86400
    )


class PredictionResponse(BaseModel):
    """Response model for predictions."""
    
    predictions: List[int] = Field(..., description="Predicted class labels")
    probabilities: List[List[float]] = Field(..., description="Class probabilities")
    model_info: Dict[str, Any] = Field(..., description="Model and prediction metadata")


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Overall service status")
    model_loaded: bool = Field(..., description="Model loading status")
    redis_connected: bool = Field(..., description="Redis connection status")
    model_name: str = Field(..., description="Loaded model name")
    version: str = Field(..., description="Service version")
    uptime: float = Field(..., description="Service uptime in seconds")


class ModelInfo(BaseModel):
    """Detailed model information."""
    
    model_name: str = Field(..., description="Model name")
    model_type: str = Field(..., description="Model type (classification/regression)")
    input_shape: List[Optional[int]] = Field(..., description="Expected input shape")
    output_classes: Optional[int] = Field(None, description="Number of output classes")
    features: List[str] = Field(..., description="Feature names")
    class_names: Optional[List[str]] = Field(None, description="Class names")
    accuracy: Optional[float] = Field(None, description="Model accuracy")
    onnx_providers: List[str] = Field(..., description="Available ONNX providers")


class BatchPredictionRequest(BaseModel):
    """Request model for batch predictions."""
    
    requests: List[PredictionRequest] = Field(
        ...,
        description="List of prediction requests",
        min_items=1,
        max_items=100
    )
    parallel: bool = Field(
        default=True,
        description="Whether to process requests in parallel"
    )


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: str = Field(..., description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")