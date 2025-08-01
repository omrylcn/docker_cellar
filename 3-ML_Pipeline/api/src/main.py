"""ML Pipeline API with ONNX Runtime, Redis caching, and monitoring."""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

import numpy as np
import onnxruntime as ort
import redis.asyncio as redis
import structlog
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel, Field

from models import PredictionRequest, PredictionResponse, HealthResponse
from utils import setup_logging, get_redis_client, ModelManager

# Setup structured logging
setup_logging()
logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter('ml_api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('ml_api_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
PREDICTION_COUNT = Counter('ml_api_predictions_total', 'Total predictions made')
MODEL_LOAD_TIME = Histogram('ml_api_model_load_seconds', 'Model loading time')

# Initialize FastAPI app
app = FastAPI(
    title="ML Pipeline API",
    description="Production-ready ML API with ONNX Runtime, Redis caching, and monitoring",
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

# Global variables
model_manager: Optional[ModelManager] = None
redis_client: Optional[redis.Redis] = None


@app.middleware("http")
async def add_process_time_header(request, call_next):
    """Add processing time and metrics to requests."""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Update Prometheus metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(process_time)
    
    return response


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global model_manager, redis_client
    
    logger.info("Starting ML Pipeline API...")
    
    # Initialize Redis client
    try:
        redis_client = await get_redis_client()
        logger.info("Redis client initialized")
    except Exception as e:
        logger.warning(f"Redis initialization failed: {e}")
        redis_client = None
    
    # Initialize model manager
    try:
        model_manager = ModelManager("models/")
        await model_manager.load_models()
        logger.info("Model manager initialized")
    except Exception as e:
        logger.error(f"Model manager initialization failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down ML Pipeline API...")
    
    if redis_client:
        await redis_client.close()
    
    logger.info("Shutdown complete")


@app.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check() -> HealthResponse:
    """Comprehensive health check endpoint."""
    model_status = model_manager is not None and model_manager.is_loaded()
    redis_status = redis_client is not None
    
    if redis_client:
        try:
            await redis_client.ping()
            redis_status = True
        except Exception:
            redis_status = False
    
    overall_status = "healthy" if model_status else "unhealthy"
    
    return HealthResponse(
        status=overall_status,
        model_loaded=model_status,
        redis_connected=redis_status,
        model_name=model_manager.get_model_name() if model_manager else "unknown",
        version="0.1.0",
        uptime=time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0
    )


@app.get("/metrics", summary="Prometheus metrics")
async def get_metrics():
    """Return Prometheus metrics."""
    return JSONResponse(
        content=generate_latest().decode('utf-8'),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/models/info", summary="Get model information")
async def get_model_info() -> Dict[str, Any]:
    """Get detailed model information."""
    if not model_manager or not model_manager.is_loaded():
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )
    
    return model_manager.get_model_info()


@app.post("/predict", response_model=PredictionResponse, summary="Make predictions")
async def predict(
    request: PredictionRequest,
    background_tasks: BackgroundTasks
) -> PredictionResponse:
    """Make predictions with optional caching."""
    if not model_manager or not model_manager.is_loaded():
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )
    
    # Generate cache key if Redis is available
    cache_key = None
    if redis_client and request.use_cache:
        cache_key = f"prediction:{hash(json.dumps(request.data, sort_keys=True))}"
        
        try:
            cached_result = await redis_client.get(cache_key)
            if cached_result:
                logger.info("Cache hit for prediction")
                return PredictionResponse.parse_raw(cached_result)
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
    
    # Make prediction
    try:
        start_time = time.time()
        predictions, probabilities = await model_manager.predict(request.data)
        prediction_time = time.time() - start_time
        
        response = PredictionResponse(
            predictions=predictions,
            probabilities=probabilities,
            model_info={
                "model_name": model_manager.get_model_name(),
                "prediction_time": prediction_time,
                "input_shape": np.array(request.data).shape,
                "cached": False
            }
        )
        
        # Cache result if Redis is available
        if redis_client and cache_key and request.use_cache:
            background_tasks.add_task(
                cache_prediction_result,
                cache_key,
                response.json(),
                request.cache_ttl
            )
        
        PREDICTION_COUNT.inc()
        
        return response
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@app.post("/predict/batch", summary="Batch predictions")
async def predict_batch(
    requests: List[PredictionRequest],
    background_tasks: BackgroundTasks
) -> List[PredictionResponse]:
    """Make batch predictions for multiple requests."""
    if not model_manager or not model_manager.is_loaded():
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )
    
    results = []
    for req in requests:
        try:
            result = await predict(req, background_tasks)
            results.append(result)
        except HTTPException as e:
            # Continue with other requests even if one fails
            logger.error(f"Batch prediction error: {e}")
            results.append(
                PredictionResponse(
                    predictions=[],
                    probabilities=[],
                    model_info={"error": str(e.detail)}
                )
            )
    
    return results


@app.post("/models/reload", summary="Reload models")
async def reload_models() -> Dict[str, str]:
    """Reload all models (useful for model updates)."""
    global model_manager
    
    try:
        if model_manager:
            await model_manager.load_models()
        else:
            model_manager = ModelManager("models/")
            await model_manager.load_models()
        
        # Clear cache if Redis is available
        if redis_client:
            try:
                await redis_client.flushdb()
                logger.info("Prediction cache cleared")
            except Exception as e:
                logger.warning(f"Cache clear error: {e}")
        
        return {
            "message": "Models reloaded successfully",
            "model_name": model_manager.get_model_name()
        }
        
    except Exception as e:
        logger.error(f"Model reload failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Model reload failed: {str(e)}"
        )


async def cache_prediction_result(cache_key: str, result: str, ttl: int):
    """Background task to cache prediction results."""
    if redis_client:
        try:
            await redis_client.setex(cache_key, ttl, result)
            logger.debug(f"Cached prediction result with key: {cache_key}")
        except Exception as e:
            logger.warning(f"Cache write error: {e}")


# Add startup time tracking
@app.middleware("http")
async def track_startup_time(request, call_next):
    if not hasattr(app.state, 'start_time'):
        app.state.start_time = time.time()
    response = await call_next(request)
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=2,
        log_level="info"
    )