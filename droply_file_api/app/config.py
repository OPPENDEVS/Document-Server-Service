from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # carpeta app/

class Config:
    # Si la variable de entorno existe
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    
    # Convertir ruta absoluta:
    if not os.path.isabs(UPLOAD_FOLDER):
        UPLOAD_FOLDER = os.path.join(BASE_DIR, UPLOAD_FOLDER)
    
    ALLOWED_EXTENSIONS = set(os.getenv("ALLOWED_EXTENSIONS", "pdf,csv").split(","))
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    SWAGGER = {
        'title': 'API de Gestión de Archivos',
        'uiversion': 3
    }
