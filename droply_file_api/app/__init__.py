import os
from flask import Flask, send_from_directory, current_app
from flasgger import Swagger
from flask_cors import CORS
from app.routes.archivo_routes import archivo_bp

def create_app():
    app = Flask(__name__)

    # Cargar configuraciones
    app.config.from_object('app.config.Config')

    # Crear carpeta de uploads si no existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Inicializar Swagger
    Swagger(app)

    # Habilitar CORS
    CORS(app)

    # Registrar Blueprints
    app.register_blueprint(archivo_bp, url_prefix="/api/archivos")

    # Servir frontend de prueba
    @app.route("/")
    def index():
        # Ruta absoluta para frontend
        frontend_path = os.path.abspath(os.path.join(current_app.root_path, '..', 'frontend'))
        return send_from_directory(frontend_path, 'index.html')

    return app
