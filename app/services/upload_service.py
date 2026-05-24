from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.utils import secure_filename


def allowed_file(filename):
    suffix = Path(filename).suffix.lower().lstrip(".")
    return suffix in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]


def allowed_media_file(filename):
    suffix = Path(filename).suffix.lower().lstrip(".")
    return suffix in current_app.config["ALLOWED_MEDIA_EXTENSIONS"]


def media_type_for(filename):
    suffix = Path(filename).suffix.lower().lstrip(".")
    if suffix in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return "image"
    if suffix in current_app.config["ALLOWED_VIDEO_EXTENSIONS"]:
        return "video"
    if suffix in current_app.config["ALLOWED_AUDIO_EXTENSIONS"]:
        return "audio"
    return "file"


def save_upload(file_storage):
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        raise ValueError("Only JPG, PNG, and WEBP images are allowed.")

    original = secure_filename(file_storage.filename)
    suffix = Path(original).suffix.lower()
    filename = f"{uuid4().hex}{suffix}"
    destination = current_app.config["UPLOAD_FOLDER"] / filename
    file_storage.save(destination)
    return f"/static/uploads/{filename}"


def save_media_upload(file_storage):
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_media_file(file_storage.filename):
        raise ValueError("Only JPG, PNG, WEBP, MP4, WEBM, MOV, MP3, WAV, OGG, and M4A files are allowed.")

    original = secure_filename(file_storage.filename)
    suffix = Path(original).suffix.lower()
    filename = f"{uuid4().hex}{suffix}"
    destination = current_app.config["UPLOAD_FOLDER"] / filename
    file_storage.save(destination)
    return {
        "url": f"/static/uploads/{filename}",
        "media_type": media_type_for(original),
        "filename": original,
    }
