import os
import uuid
from werkzeug.utils import secure_filename
from app.config import Config

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_file(file):
    if not allowed_file(file.filename):
        return None, None
    original_name = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4()}_{original_name}"
    path = os.path.join(Config.UPLOAD_FOLDER, unique_name)
    file.save(path)
    return original_name, unique_name
