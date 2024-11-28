import pymysql
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

def create_database_if_not_exists():
    """Verifica si la base de datos existe; si no, la crea."""
    db_name = os.getenv("DB_NAME")
    connection = pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=int(os.getenv("DB_PORT")),
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Base de datos '{db_name}' verificada o creada exitosamente.")
    finally:
        connection.close()

def init_db(app):
    """Inicializa SQLAlchemy y crea las tablas si no existen."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
