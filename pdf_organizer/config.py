import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "storage", "uploads")
ORGANIZED_FOLDER = os.path.join(BASE_DIR, "storage", "organized")
ALLOWED_EXTENSIONS = {".pdf"}
MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200 MB max upload