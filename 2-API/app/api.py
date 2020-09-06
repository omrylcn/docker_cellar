import os
from pathlib import Path
from flask import Flask, request, abort, jsonify, send_from_directory
from convert_func import grey_image


MODULE_PATH=Path(__file__).parent

UPLOAD_DIRECTORY = "project/api_uploaded_files"
UPLOAD_DIRECTORY=MODULE_PATH/UPLOAD_DIRECTORY

DOWNLOAD_DIRECTORY = "project/api_uploaded_files"
DOWNLOAD_DIRECTORY = MODULE_PATH/"project/api_converted_files"


os.makedirs(UPLOAD_DIRECTORY,exist_ok=True)
os.makedirs(DOWNLOAD_DIRECTORY,exist_ok=True)



api = Flask(__name__)


@api.route("/inputs")
def list_input_files():
    """Endpoint to list files on the server."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return jsonify(files)

@api.route("/outputs")
def list_output_files():
    """Endpoint to list files on the server."""
    files = []
    for filename in os.listdir(DOWNLOAD_DIRECTORY):
        path = os.path.join(DOWNLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return jsonify(files)


@api.route("/download/<path:path>")
def get_file(path):
    """Download a file."""
    return send_from_directory(DOWNLOAD_DIRECTORY, path, as_attachment=True)

@api.route("/convert")
def convert_image():
    """Convert rgb image to grey image"""
    grey_image(UPLOAD_DIRECTORY,DOWNLOAD_DIRECTORY)
    return "Converting is done"


@api.route("/upload/<filename>", methods=["POST"])
def post_file(filename):
    """Upload a file."""

    if "/" in filename:
        # Return 400 BAD REQUEST
        abort(400, "no subdirectories directories allowed")

    with open(os.path.join(UPLOAD_DIRECTORY, filename), "wb") as fp:
        fp.write(request.data)

    # Return 201 CREATED
    return "", 201


if __name__ == "__main__":
    api.run(debug=False,host='0.0.0.0', port=5000)