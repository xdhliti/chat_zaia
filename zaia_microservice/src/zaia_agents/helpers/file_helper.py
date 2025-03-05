# file_utils.py
import os
import uuid
import tempfile
from fastapi import UploadFile

def save_uploaded_file(file_in: UploadFile) -> str:
    if not file_in:
        return None
    file_bytes = file_in.file.read()
    unique_id = uuid.uuid4().hex
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, f"{unique_id}_{file_in.filename}")

    with open(file_path, "wb") as f:
        f.write(file_bytes)
    return file_path
