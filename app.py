import os
from flask import Flask, render_template, redirect, url_for
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from dotenv import load_dotenv
from database import db, create_database_if_not_exists, init_db
from controllers.heladeria_controller import heladeria_bp
from controllers.auth_controller import auth_bp
from models.usuario import Usuario, UserMixin

# Cargar configuración desde .env
load_dotenv()

# Inicializar la aplicación y especificar la carpeta de templates
app = Flask(__name__, template_folder='views')

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY', 'clave_secreta_predeterminada')

# Crear la base de datos si no existe
create_database_if_not_exists()

# Inicializar la base de datos y migraciones
init_db(app)
migrate = Migrate(app, db)

# Configurar Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'  # Redirigir si no está autenticado
login_manager.login_message = "Por favor, inicia sesión para acceder a esta página."

# Cargar usuario desde la sesión
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Ruta principal (índice)
@app.route('/')
def index():
    # Verificar si el usuario está autenticado
    if current_user.is_authenticated:
        return render_template('login.html')  # Renderiza el índice si está autenticado
    else:
        return redirect(url_for('auth.login'))  # Redirige al login si no está autenticado

# Registrar los blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(heladeria_bp, url_prefix='/heladeria')


if __name__ == '__main__':
    app.run(debug=True)
