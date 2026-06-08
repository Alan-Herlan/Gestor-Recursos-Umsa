from peewee import *
import datetime

# Definimos la base de datos SQLite
db = SqliteDatabase('institucion.db')

class BaseModel(Model):
    """Clase base que indica qué base de datos usar."""
    class Meta:
        database = db

# 1. Tabla de Usuarios (Responsables o Administradores)
class Usuario(BaseModel):
    nombre = CharField()
    email = CharField(unique=True)
    password_hash = CharField() # Aquí guardaremos la contraseña encriptada
    rol = CharField(default='usuario') # 'admin' o 'usuario'

# 2. Tabla de Ubicaciones (Laboratorios, oficinas, etc.)
class Ubicacion(BaseModel):
    nombre = CharField()
    descripcion = TextField(null=True)

# 3. Tabla de Recursos (El activo institucional)
class Recurso(BaseModel):
    nombre = CharField()
    nro_serie = CharField(unique=True)
    estado = CharField(default='Disponible') # Disponible, Asignado, Mantenimiento
    
    # Claves foráneas (Relaciones)
    ubicacion = ForeignKeyField(Ubicacion, backref='recursos')
    responsable = ForeignKeyField(Usuario, backref='recursos_asignados', null=True)

# 4. Tabla de Movimientos (Historial de transferencias)
class Movimiento(BaseModel):
    recurso = ForeignKeyField(Recurso, backref='historial_movimientos')
    usuario_origen = ForeignKeyField(Usuario, backref='entregas', null=True)
    usuario_destino = ForeignKeyField(Usuario, backref='recepciones')
    fecha_movimiento = DateTimeField(default=datetime.datetime.now)
    observaciones = TextField(null=True)

# Función para inicializar la base de datos
def crear_tablas():
    with db:
        db.create_tables([Usuario, Ubicacion, Recurso, Movimiento])
        print("Tablas creadas correctamente.")

# Si ejecutamos este archivo directamente, se crearán las tablas
if __name__ == '__main__':
    crear_tablas()