# import os
# from flask import Blueprint, request, jsonify, send_from_directory
# from app.utils.file_handler import save_file
# from app.models.archivo_model import (
#     insert_archivo, get_all_archivos, update_archivo, delete_archivo
# )
# from app.config import Config

# archivo_bp = Blueprint("archivo_bp", __name__)

# @archivo_bp.route("/subir", methods=["POST"])
# def subir():
#     archivo = request.files.get("archivo")
#     tipo = request.form.get("tipo")

#     if not archivo or not tipo:
#         return jsonify({"error": "Archivo y tipo son obligatorios"}), 400

#     nombre_original, nombre_guardado = save_file(archivo)
#     if not nombre_original:
#         return jsonify({"error": "Tipo de archivo no permitido"}), 400

#     url = os.path.join(Config.UPLOAD_FOLDER, nombre_guardado)
#     archivo_id = insert_archivo(nombre_original, url, tipo)

#     return jsonify({"mensaje": "Archivo subido", "id": archivo_id}), 201

# @archivo_bp.route("/", methods=["GET"])
# def listar():
#     archivos = get_all_archivos()
#     result = [
#         {
#             "id": row[0],
#             "nombre": row[1],
#             "url": f"/api/archivos/ver/{os.path.basename(row[2])}",
#             "creado": row[3].isoformat(),
#             "tipo": row[4]
#         } for row in archivos
#     ]
#     return jsonify(result)

# @archivo_bp.route("/ver/<filename>", methods=["GET"])
# def ver_archivo(filename):
#     return send_from_directory(Config.UPLOAD_FOLDER, filename)

# @archivo_bp.route("/descargar/<filename>", methods=["GET"])
# def descargar_archivo(filename):
#     return send_from_directory(Config.UPLOAD_FOLDER, filename, as_attachment=True)

# @archivo_bp.route("/<int:id>", methods=["PUT"])
# def editar_nombre(id):
#     nuevo_nombre = request.json.get("nombre")
#     if not nuevo_nombre:
#         return jsonify({"error": "Se requiere nuevo nombre"}), 400
#     update_archivo(id, nuevo_nombre)
#     return jsonify({"mensaje": "Nombre actualizado"})

# @archivo_bp.route("/<int:id>", methods=["DELETE"])
# def eliminar(id):
#     path = delete_archivo(id)
#     if path and os.path.exists(path):
#         os.remove(path)
#         return jsonify({"mensaje": "Archivo eliminado"}), 200
#     return jsonify({"error": "Archivo no encontrado"}), 404

import os
from flask import Blueprint, request, jsonify, send_from_directory, current_app, Response
from app.utils.file_handler import save_file
from app.models.archivo_model import (
    insert_archivo, get_all_archivos, update_archivo, delete_archivo
)
from flasgger import swag_from
import csv

archivo_bp = Blueprint("archivo_bp", __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@archivo_bp.route("/subir", methods=["POST"])
@swag_from({
    'tags': ['Archivos'],
    'parameters': [
        {
            'name': 'archivo',
            'in': 'formData',
            'type': 'file',
            'required': True
        },
        {
            'name': 'tipo',
            'in': 'formData',
            'type': 'string',
            'required': True
        }
    ],
    'responses': {
        201: {'description': 'Archivo subido exitosamente'},
        400: {'description': 'Datos inválidos o tipo de archivo no permitido'}
    }
})
def subir():
    archivo = request.files.get("archivo")
    tipo = request.form.get("tipo")

    if not archivo or not tipo:
        return jsonify({"error": "Archivo y tipo son obligatorios"}), 400

    if not allowed_file(archivo.filename):
        return jsonify({"error": "Tipo de archivo no permitido"}), 400

    nombre_original, nombre_guardado = save_file(archivo)
    url = os.path.join(current_app.config['UPLOAD_FOLDER'], nombre_guardado)
    archivo_id = insert_archivo(nombre_original, url, tipo)

    return jsonify({"mensaje": "Archivo subido", "id": archivo_id}), 201

@archivo_bp.route("/", methods=["GET"])
@swag_from({
    'tags': ['Archivos'],
    'responses': {
        200: {'description': 'Lista de archivos'}
    }
})
def listar():
    archivos = get_all_archivos()
    result = [
        {
            "id": row[0],
            "nombre": row[1],
            "url": f"/api/archivos/ver/{os.path.basename(row[2])}",
            "creado": row[3].isoformat(),
            "tipo": row[4]
        } for row in archivos
    ]
    return jsonify(result)

# @archivo_bp.route("/ver/<filename>", methods=["GET"])
# @swag_from({
#     'tags': ['Archivos'],
#     'parameters': [{'name': 'filename', 'in': 'path', 'type': 'string', 'required': True}],
#     'responses': {
#         200: {'description': 'Visualizar archivo'}
#     }
# })
# def ver_archivo(filename):
#     return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@archivo_bp.route("/ver/<filename>", methods=["GET"])
@swag_from({
    'tags': ['Archivos'],
    'parameters': [{'name': 'filename', 'in': 'path', 'type': 'string', 'required': True}],
    'responses': {
        200: {'description': 'Visualizar archivo'}
    }
})
def ver_archivo(filename):
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

    if not os.path.exists(filepath):
        return jsonify({"error": "Archivo no encontrado"}), 404

    import mimetypes
    mime_type, _ = mimetypes.guess_type(filepath)
    if not mime_type:
        mime_type = "application/octet-stream"

    if mime_type == "text/csv":
        # CSV y devolver tabla HTML
        with open(filepath, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)

        html = "<table border='1' style='border-collapse: collapse;'>"
        for i, row in enumerate(rows):
            html += "<tr>"
            for cell in row:
                if i == 0:
                    html += f"<th>{cell}</th>"
                else:
                    html += f"<td>{cell}</td>"
            html += "</tr>"
        html += "</table>"

        return Response(html, mimetype="text/html")

    else:
        return send_from_directory(
            current_app.config['UPLOAD_FOLDER'],
            filename,
            mimetype=mime_type  # visualización inline
        )

@archivo_bp.route("/descargar/<filename>", methods=["GET"])
@swag_from({
    'tags': ['Archivos'],
    'parameters': [{'name': 'filename', 'in': 'path', 'type': 'string', 'required': True}],
    'responses': {
        200: {'description': 'Descarga de archivo'}
    }
})
def descargar_archivo(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@archivo_bp.route("/<int:id>", methods=["PUT"])
@swag_from({
    'tags': ['Archivos'],
    'parameters': [
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True},
        {'name': 'body', 'in': 'body', 'schema': {'type': 'object', 'properties': {'nombre': {'type': 'string'}}}}
    ],
    'responses': {
        200: {'description': 'Nombre actualizado'},
        400: {'description': 'Nombre no enviado'}
    }
})
def editar_nombre(id):
    nuevo_nombre = request.json.get("nombre")
    if not nuevo_nombre:
        return jsonify({"error": "Se requiere nuevo nombre"}), 400
    update_archivo(id, nuevo_nombre)
    return jsonify({"mensaje": "Nombre actualizado"})

@archivo_bp.route("/<int:id>", methods=["DELETE"])
@swag_from({
    'tags': ['Archivos'],
    'parameters': [{'name': 'id', 'in': 'path', 'type': 'integer', 'required': True}],
    'responses': {
        200: {'description': 'Archivo eliminado'},
        404: {'description': 'Archivo no encontrado'}
    }
})
def eliminar(id):
    path = delete_archivo(id)
    if path and os.path.exists(path):
        os.remove(path)
        return jsonify({"mensaje": "Archivo eliminado"}), 200
    return jsonify({"error": "Archivo no encontrado"}), 404

