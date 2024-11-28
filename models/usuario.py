from flask_login import UserMixin
from database import db
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    es_admin = db.Column(db.Boolean, default=False)
    es_empleado = db.Column(db.Boolean, default=False)
    es_cliente = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        """Crea un hash seguro para la contraseña."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Verifica si la contraseña ingresada coincide con el hash almacenado."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<Usuario {self.username}>'
