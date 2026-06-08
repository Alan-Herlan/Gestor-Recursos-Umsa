# Sistema de Gestión de Recursos Institucionales

Proyecto desarrollado para la materia de [INF 133 , Carrera de Informática, UMSA.

## 1. Descripción del Proyecto
Este sistema permite la administración eficiente de activos institucionales (computadoras, proyectores, impresoras), gestionando sus responsables, ubicaciones y el historial completo de movimientos realizados.

## 2. Tecnologías Utilizadas
- **Backend:** Python con Flask
- **Base de Datos:** SQLite con ORM Peewee
- **Seguridad:** JWT (JSON Web Tokens) para protección de endpoints
- **Frontend:** HTML5, Bootstrap 5, JavaScript
- **Control de Versiones:** Git y GitHub

## 3. Instalación y Configuración
1. Clonar el repositorio: `git clone <enlace-de-tu-repo>`
2. Crear y activar entorno virtual:
   - `python -m venv env`
   - `env\Scripts\activate` (Windows)
3. Instalar dependencias: `pip install -r requirements.txt`
4. Ejecutar la aplicación: `python app.py`

## 4. Endpoints de la API
- `POST /api/login`: Obtener token JWT.
- `GET /api/recursos`: Listar activos.
- `POST /api/recursos`: Registrar activo (Requiere JWT).
- `PUT /api/recursos/<id>`: Actualizar y registrar movimiento (Requiere JWT).
- `GET /api/consultas/historial/<id>`: Consultar historial de movimientos.

## 5. Participantes
- [Tu Nombre]
- [Nombre de tu compañero]

---
*Gestión 2026 - Carrera de Informática UMSA*