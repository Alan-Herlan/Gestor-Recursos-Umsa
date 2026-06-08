from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
import os

# Importamos la base de datos y los modelos que creaste
from models import db, Usuario, Ubicacion, Recurso, Movimiento

# Cargar las variables del archivo .env
load_dotenv()

# Inicializar la aplicación Flask
app = Flask(__name__)
CORS(app) # Permite que el frontend (HTML/JS) se comunique con esta API

# Configuración de seguridad JWT
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'clave-de-respaldo')
jwt = JWTManager(app)

# ==========================================
# MANEJO DE CONEXIÓN A LA BASE DE DATOS
# ==========================================
# Peewee requiere abrir la conexión antes de cada petición y cerrarla al terminar.

@app.before_request
def before_request():
    db.connect()

@app.after_request
def after_request(response):
    if not db.is_closed():
        db.close()
    return response

# ==========================================
# ENDPOINT DE PRUEBA
# ==========================================

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "estado": "operativo",
        "mensaje": "API de Gestión de Recursos Institucionales funcionando correctamente."
    })

# ==========================================
# ARRANQUE DEL SERVIDOR
# ==========================================
if __name__ == '__main__':
    # debug=True permite que el servidor se reinicie solo si haces cambios en el código
    app.run(debug=True, port=5000)