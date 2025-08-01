"""Utility functions for ML Pipeline API."""

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

import numpy as np
import onnxruntime as ort
import redis.asyncio as redis
import structlog


def setup_logging():
    """Configure structured logging."""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


async def get_redis_client() -> redis.Redis:
    """Get Redis client with connection pooling."""
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    client = redis.from_url(
        redis_url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=20,
        retry_on_timeout=True,
        socket_keepalive=True,
        socket_keepalive_options={},
    )
    
    # Test connection
    await client.ping()
    return client


class ModelManager:
    """ONNX model manager with async support."""
    
    def __init__(self, models_dir: str):
        self.models_dir = Path(models_dir)
        self.session: Optional[ort.InferenceSession] = None
        self.metadata: Dict[str, Any] = {}
        self.logger = structlog.get_logger(__name__)
        
    async def load_models(self):
        """Load ONNX models and metadata."""
        model_files = list(self.models_dir.glob("*.onnx"))
        
        if not model_files:
            raise FileNotFoundError(f"No ONNX models found in {self.models_dir}")
        
        # Load the first model found (extend for multiple models)
        model_path = model_files[0]
        metadata_path = self.models_dir / "model_metadata.json"
        
        start_time = time.time()
        
        try:
            # Load ONNX model
            self.session = ort.InferenceSession(
                str(model_path),
                providers=['CPUExecutionProvider'],
                sess_options=self._get_session_options()
            )
            
            # Load metadata
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = {
                    "model_name": model_path.stem,
                    "model_type": "unknown"
                }
            
            load_time = time.time() - start_time
            self.logger.info(
                "Model loaded successfully",
                model_name=self.metadata.get("model_name"),
                load_time=load_time
            )
            
        except Exception as e:
            self.logger.error("Failed to load model", error=str(e))
            raise
    
    def _get_session_options(self) -> ort.SessionOptions:
        """Configure ONNX Runtime session options."""
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        sess_options.enable_cpu_mem_arena = True
        sess_options.enable_mem_pattern = True
        sess_options.enable_mem_reuse = True
        
        # Configure thread settings
        sess_options.intra_op_num_threads = min(4, os.cpu_count() or 1)
        sess_options.inter_op_num_threads = min(2, os.cpu_count() or 1)
        
        return sess_options
    
    async def predict(self, data: List[List[float]]) -> Tuple[List[int], List[List[float]]]:
        """Make async predictions."""
        if not self.session:
            raise ValueError("Model not loaded")
        
        # Convert to numpy array
        input_data = np.array(data, dtype=np.float32)
        
        # Validate input shape
        expected_features = self.metadata.get("input_shape", [None, None])[1]
        if expected_features and input_data.shape[1] != expected_features:
            raise ValueError(
                f"Invalid input shape. Expected {expected_features} features, "
                f"got {input_data.shape[1]}"
            )
        
        # Get input name
        input_name = self.session.get_inputs()[0].name
        
        # Run inference in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        outputs = await loop.run_in_executor(
            None,
            lambda: self.session.run(None, {input_name: input_data})
        )
        
        # Extract predictions and probabilities
        predictions = outputs[0].tolist()
        probabilities = outputs[1].tolist() if len(outputs) > 1 else []
        
        return predictions, probabilities
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.session is not None
    
    def get_model_name(self) -> str:
        """Get model name."""
        return self.metadata.get("model_name", "unknown")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get comprehensive model information."""
        if not self.session:
            return {"error": "Model not loaded"}
        
        # Get ONNX model info
        model_inputs = [
            {
                "name": input_meta.name,
                "type": str(input_meta.type),
                "shape": input_meta.shape
            }
            for input_meta in self.session.get_inputs()
        ]
        
        model_outputs = [
            {
                "name": output_meta.name,
                "type": str(output_meta.type),
                "shape": output_meta.shape
            }
            for output_meta in self.session.get_outputs()
        ]
        
        return {
            **self.metadata,
            "onnx_inputs": model_inputs,
            "onnx_outputs": model_outputs,
            "providers": self.session.get_providers(),
            "session_options": {
                "graph_optimization_level": "ORT_ENABLE_ALL",
                "intra_op_num_threads": self.session.get_session_options().intra_op_num_threads,
                "inter_op_num_threads": self.session.get_session_options().inter_op_num_threads
            }
        }


class MetricsCollector:
    """Custom metrics collector for model performance."""
    
    def __init__(self):
        self.prediction_times: List[float] = []
        self.prediction_counts = 0
        self.error_counts = 0
        self.cache_hits = 0
        self.cache_misses = 0
    
    def record_prediction(self, duration: float, success: bool = True):
        """Record prediction metrics."""
        self.prediction_times.append(duration)
        if success:
            self.prediction_counts += 1
        else:
            self.error_counts += 1
    
    def record_cache_hit(self):
        """Record cache hit."""
        self.cache_hits += 1
    
    def record_cache_miss(self):
        """Record cache miss."""
        self.cache_misses += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if not self.prediction_times:
            return {"message": "No predictions recorded yet"}
        
        return {
            "total_predictions": self.prediction_counts,
            "total_errors": self.error_counts,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0,
            "avg_prediction_time": np.mean(self.prediction_times),
            "min_prediction_time": np.min(self.prediction_times),
            "max_prediction_time": np.max(self.prediction_times),
            "p95_prediction_time": np.percentile(self.prediction_times, 95),
            "p99_prediction_time": np.percentile(self.prediction_times, 99)
        }


def validate_input_data(data: List[List[float]], expected_features: int) -> bool:
    """Validate input data format and shape."""
    if not data:
        return False
    
    if not all(isinstance(row, list) for row in data):
        return False
    
    if not all(len(row) == expected_features for row in data):
        return False
    
    if not all(isinstance(val, (int, float)) for row in data for val in row):
        return False
    
    return True


async def health_check_dependencies() -> Dict[str, bool]:
    """Check health of all dependencies."""
    results = {}
    
    # Check Redis
    try:
        redis_client = await get_redis_client()
        await redis_client.ping()
        await redis_client.close()
        results["redis"] = True
    except Exception:
        results["redis"] = False
    
    # Add other dependency checks here (database, external APIs, etc.)
    
    return results