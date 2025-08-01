"""Image conversion utilities for RGB to grayscale processing."""

import os
from pathlib import Path
from typing import List, Optional

from skimage.io import imread, imsave
from skimage.color import rgb2gray
import numpy as np


def convert_images_to_grayscale(
    input_path: str, 
    output_path: str,
    supported_extensions: Optional[List[str]] = None
) -> int:
    """Convert all RGB images in input directory to grayscale.
    
    Args:
        input_path: Directory containing input images
        output_path: Directory to save converted images
        supported_extensions: List of supported file extensions
        
    Returns:
        Number of successfully converted images
        
    Raises:
        FileNotFoundError: If input directory doesn't exist
        ValueError: If there's an error processing images
    """
    if supported_extensions is None:
        supported_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    
    input_dir = Path(input_path)
    output_dir = Path(output_path)
    
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_path}")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    converted_count = 0
    errors = []
    
    for file_path in input_dir.iterdir():
        if not file_path.is_file():
            continue
            
        # Check if file extension is supported
        if file_path.suffix.lower() not in supported_extensions:
            continue
            
        try:
            # Read and convert image
            image = imread(str(file_path))
            
            # Skip if already grayscale (2D array)
            if len(image.shape) == 2:
                print(f"Skipping {file_path.name}: already grayscale")
                continue
                
            # Convert to grayscale
            grayscale_image = rgb2gray(image)
            
            # Generate output filename
            stem = file_path.stem
            suffix = file_path.suffix
            output_filename = f"{stem}_grayscale{suffix}"
            output_file_path = output_dir / output_filename
            
            # Save converted image
            imsave(str(output_file_path), grayscale_image)
            
            converted_count += 1
            print(f"Converted: {file_path.name} -> {output_filename}")
            
        except Exception as e:
            error_msg = f"Error converting {file_path.name}: {str(e)}"
            errors.append(error_msg)
            print(error_msg)
            continue
    
    if errors:
        print(f"\nConversion completed with {len(errors)} errors:")
        for error in errors:
            print(f"  - {error}")
    
    return converted_count


def validate_image_file(file_path: Path) -> bool:
    """Validate if file is a supported image format.
    
    Args:
        file_path: Path to the image file
        
    Returns:
        True if file is a valid image, False otherwise
    """
    supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    
    if not file_path.exists() or not file_path.is_file():
        return False
        
    if file_path.suffix.lower() not in supported_extensions:
        return False
        
    try:
        # Try to read the image to validate format
        image = imread(str(file_path))
        return image is not None and len(image.shape) >= 2
    except Exception:
        return False


# Legacy function name for backward compatibility
def grey_image(input_path: str, output_path: str) -> int:
    """Legacy function name. Use convert_images_to_grayscale instead."""
    return convert_images_to_grayscale(input_path, output_path)