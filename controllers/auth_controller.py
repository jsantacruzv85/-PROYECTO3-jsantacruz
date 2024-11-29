from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from models.usuario import Usuario, UserMixin
from database import db
import jwt
import datetime
from functools import wraps
from werkzeug.security import generate_password_hash
import os

# Cargar la clave secreta desde .env
SECRET_KEY = os.getenv('SECRET_KEY', 'clave_secreta_default')  # Valor predeterminado si no está configurado

# Crear el blueprint para rutas de autenticación
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Decorador para proteger endpoints con JWT (para la API)
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'error': 'Token requerido'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            # Obtener usuario desde la base de datos
            user = Usuario.query.get(data['user_id'])
            if not user:
                return jsonify({'error': 'Usuario no encontrado'}), 404

            # Asignar atributos de roles al usuario actual
            user.es_admin = data.get('es_admin', False)
            user.es_empleado = data.get('es_empleado', False)
            user.es_cliente = data.get('es_cliente', False)
            
            # Usar el usuario para la función decorada
            return f(user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'El token ha expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401

    return decorated

# Decorador para verificar roles específicos
def check_roles(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verificar si el usuario tiene al menos uno de los roles permitidos
            print("Usuario actual:", current_user.username, current_user.__dict__)  # Depuración
            if not any(getattr(current_user, f'es_{role}', False) for role in roles):
                raise PermissionError("No autorizado")
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Decorador para verificar roles API
def role_required_api(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            if not any(getattr(current_user, f'es_{role}', False) for role in roles):
                return jsonify({'error': 'No autorizado'}), 403
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator

# Decorador para verificar roles en el frontend
def role_required_html(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Verificar roles usando el decorador base
                check_roles(*roles)(f)(*args, **kwargs)
            except PermissionError:
                abort(403)  # Renderiza automáticamente 403.html
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# **Ruta de Login (Formulario HTML y API)**
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Manejar credenciales desde formulario o JSON
        username = request.form.get('username') or request.json.get('username')
        password = request.form.get('password') or request.json.get('password')

        usuario = Usuario.query.filter_by(username=username).first()
        if usuario and usuario.check_password(password):
            login_user(usuario)

            if request.is_json:
                token = jwt.encode({
                    'user_id': usuario.id,
                    'es_admin': usuario.es_admin,
                    'es_empleado': usuario.es_empleado,
                    'es_cliente': usuario.es_cliente,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                }, SECRET_KEY, algorithm='HS256')
                return jsonify({'message': 'Inicio de sesión exitoso', 'token': token}), 200
            else:
                flash('Inicio de sesión exitoso', 'success')
                return redirect(url_for('heladeria.pagina_listar_productos'))

        # Manejar errores de inicio de sesión
        if request.is_json:
            return jsonify({'error': 'Credenciales inválidas'}), 401
        else:
            flash('Credenciales inválidas', 'error')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

# **Ruta de Login para la API (Solo JSON)**
@auth_bp.route('/api_login', methods=['POST'])
def api_login():
    """
    Login de usuario y generación de token JWT.
    """
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Faltan campos en la solicitud'}), 400

    username = data.get('username')
    password = data.get('password')

    usuario = Usuario.query.filter_by(username=username).first()
    if not usuario or not usuario.check_password(password):
        return jsonify({'error': 'Credenciales inválidas'}), 401

    token = jwt.encode({
        'user_id': usuario.id,
        'es_admin': usuario.es_admin,
        'es_empleado': usuario.es_empleado,
        'es_cliente': usuario.es_cliente,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, SECRET_KEY, algorithm='HS256')

    return jsonify({'token': token, 'message': f'Bienvenido, {username}!'}), 200

# **Registrar nuevos usuarios (solo admins)**
@auth_bp.route('/register', methods=['POST'])
@token_required
@role_required_api('admin')
def register(current_user):
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    es_admin = data.get('es_admin', False)
    es_empleado = data.get('es_empleado', False)
    es_cliente = data.get('es_cliente', False)

    if Usuario.query.filter_by(username=username).first():
        return jsonify({'error': 'El usuario ya existe'}), 400

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

# **Ruta protegida de ejemplo**
@auth_bp.route('/protegido', methods=['GET'])
@login_required
def protegido():
    return jsonify({'message': f'Hola, {current_user.username}. Este es un endpoint protegido.'})

# **Ruta protegida solo para administradores**
@auth_bp.route('/solo-admin', methods=['GET'])
@login_required
@role_required_api('admin')
def solo_admin(current_user):
    return jsonify({'message': f'Hola, {current_user.username}. Este es un endpoint solo para administradores.'})

# **Cerrar sesión**
@auth_bp.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('auth.login'))
