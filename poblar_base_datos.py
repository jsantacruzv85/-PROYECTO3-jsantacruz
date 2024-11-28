from models.usuario import Usuario
from models.producto import Producto
from models.ingrediente import Ingrediente
from database import db
from werkzeug.security import generate_password_hash
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import os

# Cargar configuración desde .env
load_dotenv()

# Inicializar la aplicación para acceder al contexto
app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos
db.init_app(app)

# Función para registrar usuarios
@app.route('/register', methods=['POST'])
def register_user():
    """
    Endpoint para registrar un nuevo usuario.
    Requiere un JSON con: username, password, roles (es_admin, es_empleado, es_cliente).
    """
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        es_admin = data.get('es_admin', False)
        es_empleado = data.get('es_empleado', False)
        es_cliente = data.get('es_cliente', False)

        if Usuario.query.filter_by(username=username).first():
            return jsonify({'error': 'El usuario ya existe'}), 400

        # Hashear la contraseña
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        nuevo_usuario = Usuario(
            username=username,
            password=hashed_password,
            es_admin=es_admin,
            es_empleado=es_empleado,
            es_cliente=es_cliente
        )
        db.session.add(nuevo_usuario)
        db.session.commit()

        return jsonify({'message': f'Usuario {username} creado exitosamente'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Ocurrió un error: {str(e)}'}), 500


# Función para poblar la base de datos
def poblar_base_datos():
    with app.app_context():
        try:
            # Crear usuarios
            print("\n--- Poblando usuarios ---")
            if not Usuario.query.filter_by(username="admin").first():
                hashed_password = generate_password_hash("admin123", method='pbkdf2:sha256')
                admin_user = Usuario(username="admin", password=hashed_password, es_admin=True, es_empleado=False, es_cliente=False)
                db.session.add(admin_user)
                print("Usuario administrador creado.")
            else:
                print("El usuario administrador ya existe.")

            if not Usuario.query.filter_by(username="empleado").first():
                hashed_password = generate_password_hash("empleado123", method='pbkdf2:sha256')
                empleado_user = Usuario(username="empleado", password=hashed_password, es_admin=False, es_empleado=True, es_cliente=False)
                db.session.add(empleado_user)
                print("Usuario empleado creado.")
            else:
                print("El usuario empleado ya existe.")

            if not Usuario.query.filter_by(username="cliente").first():
                hashed_password = generate_password_hash("cliente123", method='pbkdf2:sha256')
                cliente_user = Usuario(username="cliente", password=hashed_password, es_admin=False, es_empleado=False, es_cliente=True)
                db.session.add(cliente_user)
                print("Usuario cliente creado.")
            else:
                print("El usuario cliente ya existe.")

            # Crear ingredientes
            print("\n--- Poblando ingredientes ---")
            ingredientes = [
                {"nombre": "Chocolate", "precio": 5.0, "calorias": 120, "inventario": 50, "es_vegetariano": True},
                {"nombre": "Fresa", "precio": 4.0, "calorias": 90, "inventario": 30, "es_vegetariano": True},
                {"nombre": "Leche", "precio": 3.0, "calorias": 150, "inventario": 100, "es_vegetariano": False}
            ]

            for data in ingredientes:
                if not Ingrediente.query.filter_by(nombre=data["nombre"]).first():
                    nuevo_ingrediente = Ingrediente(**data)
                    db.session.add(nuevo_ingrediente)
                    print(f"Ingrediente '{data['nombre']}' creado.")
                else:
                    print(f"El ingrediente '{data['nombre']}' ya existe.")

            # Crear productos
            print("\n--- Poblando productos ---")
            productos = [
                {"nombre": "Helado de Chocolate", "precio_publico": 15.0, "calorias_totales": 200, "costo_produccion": 8.0, "rentabilidad": 0.0},
                {"nombre": "Helado de Fresa", "precio_publico": 12.0, "calorias_totales": 180, "costo_produccion": 7.0, "rentabilidad": 0.0},
                {"nombre": "Batido Mixto", "precio_publico": 20.0, "calorias_totales": 250, "costo_produccion": 10.0, "rentabilidad": 0.0}
            ]

            for data in productos:
                if not Producto.query.filter_by(nombre=data["nombre"]).first():
                    nuevo_producto = Producto(**data)
                    db.session.add(nuevo_producto)
                    print(f"Producto '{data['nombre']}' creado.")
                else:
                    print(f"El producto '{data['nombre']}' ya existe.")

            # Confirmar los cambios
            db.session.commit()
            print("\nBase de datos poblada exitosamente.")
        except Exception as e:
            db.session.rollback()
            print(f"Error durante el proceso de poblar la base de datos: {e}")


if __name__ == "__main__":
    poblar_base_datos()
