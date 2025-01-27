from typing import List
from uuid import uuid4
from flask import request, jsonify, abort
from util_functions import upload_file_to_imagekit

def file_uploads():
    if 'files' not in request.files:
        abort(400, "No files found in the request")

    files = request.files.getlist('files')  # Get the list of files
    uploaded_file_paths: List[str] = []

    for file in files:
        if file.filename == "":
            abort(400, "One of the files does not have a filename")

        # create new file name
        local_new_file_path = f"uploads/{uuid4()}.{file.mimetype.split("/").pop()}"

        file.save(local_new_file_path)
        new_file_path = upload_file_to_imagekit(local_new_file_path)
        print(f"new_file_path ==> {new_file_path}")
        uploaded_file_paths.append(new_file_path)

    return jsonify({
        "success": True,
        "code": 200,
        "message": "File(s) uploaded",
        "data": uploaded_file_paths,
    })

def file_uploads_save_on_disk():
    if 'files' not in request.files:
        abort(400, "No files found in the request")
    files = request.files.getlist('files')  # Get the list of files
    uploaded_file_paths = []

    for file in files:
        if file.filename == "":
            abort(400, "One of the files does not have a filename")

        # create new file name
        new_file_path = f"uploads/{uuid4()}.{file.mimetype.split("/").pop()}"
        file.save(new_file_path)
        uploaded_file_paths.append(new_file_path)

    return jsonify({
        "success": True,
        "code": 200,
        "message": "File(s) uploaded",
        "data": uploaded_file_paths,
    })
