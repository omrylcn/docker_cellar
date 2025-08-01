"""FastAPI service for image processing with upload/download capabilities."""

import os
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from convert_func import convert_images_to_grayscale


# Initialize FastAPI app
app = FastAPI(
    title="Image Processing API",
    description="FastAPI service for converting images to grayscale",
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

# Directory configuration
MODULE_PATH = Path(__file__).parent
UPLOAD_DIRECTORY = MODULE_PATH / "project" / "api_uploaded_files"
DOWNLOAD_DIRECTORY = MODULE_PATH / "project" / "api_converted_files"

# Ensure directories exist
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
DOWNLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)


@app.get("/", summary="Health check")
async def root() -> dict:
    """Health check endpoint."""
    return {
        "message": "Image Processing API is running",
        "status": "healthy",
        "version": "0.1.0"
    }


@app.get("/inputs", response_model=List[str], summary="List uploaded files")
async def list_input_files() -> List[str]:
    """List all uploaded input files."""
    try:
        files = [
            f.name for f in UPLOAD_DIRECTORY.iterdir() 
            if f.is_file() and not f.name.startswith('.')
        ]
        return sorted(files)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing input files: {str(e)}"
        )


@app.get("/outputs", response_model=List[str], summary="List converted files")
async def list_output_files() -> List[str]:
    """List all converted output files."""
    try:
        files = [
            f.name for f in DOWNLOAD_DIRECTORY.iterdir() 
            if f.is_file() and not f.name.startswith('.')
        ]
        return sorted(files)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing output files: {str(e)}"
        )


@app.get("/download/{filename}", summary="Download converted file")
async def download_file(filename: str) -> FileResponse:
    """Download a converted file."""
    if "/" in filename or ".." in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename: no subdirectories allowed"
        )
    
    file_path = DOWNLOAD_DIRECTORY / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{filename}' not found"
        )
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )


@app.post("/convert", summary="Convert uploaded images to grayscale")
async def convert_images() -> dict:
    """Convert all uploaded RGB images to grayscale."""
    try:
        # Check if there are any input files
        input_files = list(UPLOAD_DIRECTORY.glob("*"))
        if not input_files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files found to convert. Please upload files first."
            )
        
        # Convert images
        converted_count = convert_images_to_grayscale(
            str(UPLOAD_DIRECTORY), 
            str(DOWNLOAD_DIRECTORY)
        )
        
        return {
            "message": "Conversion completed successfully",
            "converted_files": converted_count,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during conversion: {str(e)}"
        )


@app.post("/upload", summary="Upload image file")
async def upload_file(file: UploadFile = File(...)) -> dict:
    """Upload an image file for processing."""
    
    # Validate filename
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    if "/" in file.filename or ".." in file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename: no subdirectories allowed"
        )
    
    # Validate file type (basic check)
    allowed_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Save uploaded file
        file_path = UPLOAD_DIRECTORY / file.filename
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "message": f"File '{file.filename}' uploaded successfully",
            "filename": file.filename,
            "size": len(content),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )