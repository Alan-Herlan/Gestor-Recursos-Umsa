from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from playhouse.shortcuts import model_to_dict
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
    return render_template('index.html')
# ==========================================
# 1. AUTENTICACIÓN Y SEGURIDAD
# ==========================================

@app.route('/api/registro', methods=['POST'])
def registrar_usuario():
    datos = request.get_json()
    
    # Validar si el correo ya existe
    if Usuario.select().where(Usuario.email == datos['email']).exists():
        return jsonify({"error": "El email ya está registrado"}), 400
    
    # Guardar usuario con contraseña encriptada
    nuevo_usuario = Usuario.create(
        nombre=datos['nombre'],
        email=datos['email'],
        password_hash=generate_password_hash(datos['password']),
        rol=datos.get('rol', 'usuario')
    )
    return jsonify({"mensaje": "Usuario creado exitosamente", "id": nuevo_usuario.id}), 201

@app.route('/api/login', methods=['POST'])
def login():
    datos = request.get_json()
    usuario = Usuario.get_or_none(Usuario.email == datos['email'])
    
    # Verificar que el usuario exista y la contraseña coincida
    if usuario and check_password_hash(usuario.password_hash, datos['password']):
        # Se genera el Token que actúa como "llave" para las rutas protegidas
        token = create_access_token(identity=str(usuario.id))
        return jsonify({"token": token, "usuario": usuario.nombre, "rol": usuario.rol}), 200
    
    return jsonify({"error": "Credenciales inválidas"}), 401

# ==========================================
# 2. OPERACIONES CRUD: RECURSOS
# ==========================================

# GET: Lista todos los recursos (Ruta pública)
@app.route('/api/recursos', methods=['GET'])
def obtener_recursos():
    # model_to_dict convierte el objeto de Peewee en un diccionario apto para JSON
    recursos = [model_to_dict(r) for r in Recurso.select()]
    return jsonify(recursos), 200

# POST: Crea un recurso nuevo (Ruta PROTEGIDA con JWT)
@app.route('/api/recursos', methods=['POST'])
@jwt_required()
def crear_recurso():
    datos = request.get_json()
    usuario_id = get_jwt_identity() # Obtiene el ID del usuario desde el Token
    
    try:
        nuevo_recurso = Recurso.create(
            nombre=datos['nombre'],
            nro_serie=datos['nro_serie'],
            estado=datos.get('estado', 'Disponible'),
            ubicacion=datos['ubicacion_id'],
            responsable=usuario_id # Automáticamente asigna a quien hizo la petición
        )
        return jsonify({"mensaje": "Recurso registrado", "id": nuevo_recurso.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# DELETE: Elimina un recurso (Ruta PROTEGIDA con JWT)
@app.route('/api/recursos/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_recurso(id):
    recurso = Recurso.get_or_none(Recurso.id == id)
    if not recurso:
        return jsonify({"error": "Recurso no encontrado"}), 404
        
    recurso.delete_instance()
    return jsonify({"mensaje": "Recurso eliminado correctamente"}), 200

# ==========================================
# 3. GESTIÓN DE MOVIMIENTOS Y ASIGNACIONES (PUT)
# ==========================================

# PUT: Actualizar un recurso (Cambiar responsable, ubicación o estado)
# PROTEGIDA con JWT. Resuelve Problemas 2 y 4.
@app.route('/api/recursos/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_recurso(id):
    recurso = Recurso.get_or_none(Recurso.id == id)
    if not recurso:
        return jsonify({"error": "Recurso no encontrado"}), 404
        
    datos = request.get_json()
    usuario_operador_id = get_jwt_identity() # Quién hace el cambio
    
    # Guardamos los estados anteriores para el historial
    responsable_anterior = recurso.responsable.id if recurso.responsable else None
    ubicacion_anterior = recurso.ubicacion.id if recurso.ubicacion else None

    # Actualizamos los campos si vienen en la petición
    if 'nombre' in datos: recurso.nombre = datos['nombre']
    if 'estado' in datos: recurso.estado = datos['estado']
    if 'ubicacion_id' in datos: recurso.ubicacion = datos['ubicacion_id']
    if 'responsable_id' in datos: recurso.responsable = datos['responsable_id']
    
    recurso.save() # Guarda los cambios en la BD

    # Si hubo cambio de responsable o ubicación, registramos el Movimiento automáticamente
    if ('responsable_id' in datos and datos['responsable_id'] != responsable_anterior) or \
       ('ubicacion_id' in datos and datos['ubicacion_id'] != ubicacion_anterior):
        
        Movimiento.create(
            recurso=recurso.id,
            usuario_origen=responsable_anterior,
            usuario_destino=datos.get('responsable_id', responsable_anterior),
            observaciones=datos.get('observaciones', 'Cambio de asignación o ubicación desde la API.')
        )

    return jsonify({"mensaje": "Recurso actualizado e historial registrado correctamente"}), 200


# ==========================================
# 4. CONSULTAS PERSONALIZADAS
# ==========================================

# GET: Consultar activos por ubicación específica. Resuelve Problema 3.
@app.route('/api/consultas/ubicacion/<int:ubicacion_id>', methods=['GET'])
def recursos_por_ubicacion(ubicacion_id):
    recursos = [model_to_dict(r) for r in Recurso.select().where(Recurso.ubicacion == ubicacion_id)]
    return jsonify(recursos), 200


# GET: Obtener el historial completo de movimientos de un activo. Requisito Mínimo 6.
@app.route('/api/consultas/historial/<int:recurso_id>', methods=['GET'])
def historial_recurso(recurso_id):
    movimientos = [model_to_dict(m) for m in Movimiento.select().where(Movimiento.recurso == recurso_id)]
    return jsonify(movimientos), 200

# ==========================================
# 5. RUTAS AUXILIARES (UBICACIONES Y USUARIOS)
# ==========================================

# GET: Listar todas las ubicaciones
@app.route('/api/ubicaciones', methods=['GET'])
def obtener_ubicaciones():
    ubicaciones = [model_to_dict(u) for u in Ubicacion.select()]
    return jsonify(ubicaciones), 200

# POST: Crear una nueva ubicación (Protegida con JWT)
@app.route('/api/ubicaciones', methods=['POST'])
@jwt_required()
def crear_ubicacion():
    datos = request.get_json()
    try:
        nueva_ubicacion = Ubicacion.create(
            nombre=datos['nombre'],
            descripcion=datos.get('descripcion', '')
        )
        return jsonify({"mensaje": "Ubicación creada exitosamente", "id": nueva_ubicacion.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# DELETE: Eliminar una ubicación (Protegida con JWT)
@app.route('/api/ubicaciones/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_ubicacion(id):
    ubicacion = Ubicacion.get_or_none(Ubicacion.id == id)
    if not ubicacion:
        return jsonify({"error": "Ubicación no encontrada"}), 404
        
    ubicacion.delete_instance()
    return jsonify({"mensaje": "Ubicación eliminada correctamente"}), 200

# GET: Listar todos los usuarios (Útil para el frontend al asignar responsables)
@app.route('/api/usuarios', methods=['GET'])
def obtener_usuarios():
    # model_to_dict permite excluir campos. ¡Nunca enviamos el password_hash al frontend!
    usuarios = [model_to_dict(u, exclude=[Usuario.password_hash]) for u in Usuario.select()]
    return jsonify(usuarios), 200
# ==========================================
# ARRANQUE DEL SERVIDOR
# ==========================================
if __name__ == '__main__':
    # debug=True permite que el servidor se reinicie solo si haces cambios en el código
    app.run(debug=True, port=5000)