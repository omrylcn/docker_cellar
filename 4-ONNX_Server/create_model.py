"""Create a simple ONNX model for demonstration purposes."""

import numpy as np
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import onnx
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import pickle
from pathlib import Path


def create_sample_model():
    """Create and save a sample Random Forest model in ONNX format."""
    
    # Create sample dataset
    print("Creating sample dataset...")
    X, y = make_classification(
        n_samples=1000,
        n_features=10,
        n_informative=8,
        n_redundant=2,
        n_classes=3,
        random_state=42
    )
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    print("Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        max_depth=10
    )
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy:.4f}")
    
    # Convert to ONNX
    print("Converting to ONNX format...")
    initial_type = [('float_input', FloatTensorType([None, X.shape[1]]))]
    onnx_model = convert_sklearn(
        model, 
        initial_types=initial_type,
        target_opset=12
    )
    
    # Create models directory
    models_dir = Path("app/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Save ONNX model
    onnx_path = models_dir / "random_forest_classifier.onnx"
    with open(onnx_path, "wb") as f:
        f.write(onnx_model.SerializeToString())
    
    # Save model metadata
    metadata = {
        "model_name": "random_forest_classifier",
        "model_type": "classification",
        "input_shape": [None, X.shape[1]],
        "output_classes": 3,
        "accuracy": accuracy,
        "features": [f"feature_{i}" for i in range(X.shape[1])],
        "class_names": ["class_0", "class_1", "class_2"]
    }
    
    metadata_path = models_dir / "model_metadata.json"
    import json
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    
    # Save sample test data
    sample_data = {
        "test_input": X_test[:5].tolist(),
        "expected_output": y_test[:5].tolist()
    }
    
    sample_path = models_dir / "sample_data.json"
    with open(sample_path, "w") as f:
        json.dump(sample_data, f, indent=2)
    
    print(f"✅ ONNX model saved to: {onnx_path}")
    print(f"✅ Metadata saved to: {metadata_path}")
    print(f"✅ Sample data saved to: {sample_path}")
    
    return onnx_path, metadata


if __name__ == "__main__":
    create_sample_model()