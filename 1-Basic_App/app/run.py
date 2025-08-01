"""Basic image converter: RGB to grayscale using scikit-image."""

import json
from pathlib import Path
from typing import Dict, Any

from skimage.io import imread, imsave
from skimage.color import rgb2gray


def load_parameters(param_file: Path) -> Dict[str, Any]:
    """Load processing parameters from JSON file.
    
    Args:
        param_file: Path to the JSON parameter file
        
    Returns:
        Dictionary containing processing parameters
        
    Raises:
        FileNotFoundError: If parameter file doesn't exist
        json.JSONDecodeError: If parameter file is invalid JSON
    """
    try:
        with open(param_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Parameter file not found: {param_file}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in parameter file: {e}")


def convert_to_grayscale(input_path: Path, output_path: Path) -> None:
    """Convert RGB image to grayscale.
    
    Args:
        input_path: Path to input RGB image
        output_path: Path where grayscale image will be saved
        
    Raises:
        FileNotFoundError: If input image doesn't exist
        ValueError: If image format is not supported
    """
    try:
        # Read RGB image
        image = imread(input_path)
        
        # Convert to grayscale
        grayscale_image = rgb2gray(image)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save grayscale image
        imsave(output_path, grayscale_image)
        
        print(f"Successfully converted {input_path} -> {output_path}")
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Input image not found: {input_path}")
    except Exception as e:
        raise ValueError(f"Error processing image: {e}")


def main() -> None:
    """Main function to run the image conversion process."""
    param_file = Path("data/param/parameters.json")
    
    try:
        # Load parameters
        params = load_parameters(param_file)
        
        input_path = Path(params["input_directory"])
        output_path = Path(params["output_directory"])
        
        # Convert image
        convert_to_grayscale(input_path, output_path)
        
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()

