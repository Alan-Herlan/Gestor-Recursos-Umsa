from models import db, Usuario, Ubicacion, Recurso, Movimiento, crear_tablas
from werkzeug.security import generate_password_hash

def sembrar_datos():
    # 1. Primero creamos las tablas
    crear_tablas()
    
    with db:
        # 2. Creamos los datos
        lab1 = Ubicacion.create(nombre="Laboratorio 1", descripcion="Piso 2, Edificio Central")
        lab2 = Ubicacion.create(nombre="Laboratorio 2", descripcion="Piso 3, Edificio Central")
        oficina = Ubicacion.create(nombre="Oficina de Sistemas", descripcion="Bloque Administrativo")

        admin = Usuario.create(
            nombre="Administrador UMSA", 
            email="admin@umsa.edu", 
            password_hash=generate_password_hash("123456"), 
            rol="admin"
        )
        
        Recurso.create(nombre="Proyector EPSON", nro_serie="EPS-001", ubicacion=lab1, responsable=admin)
        Recurso.create(nombre="PC HP Pavilion", nro_serie="HP-998", ubicacion=lab1, responsable=admin)
        Recurso.create(nombre="Switch CISCO", nro_serie="CIS-445", ubicacion=oficina, responsable=admin)
        Recurso.create(nombre="Laptop Lenovo", nro_serie="LEN-112", ubicacion=lab2, responsable=admin)
        Recurso.create(nombre="Monitor Samsung", nro_serie="SAM-556", ubicacion=lab2, responsable=admin)

        print("Base de datos creada y poblada correctamente.")

if __name__ == '__main__':
    sembrar_datos()