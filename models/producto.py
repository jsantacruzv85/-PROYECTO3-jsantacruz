from database import db

class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    precio_publico = db.Column(db.Float, nullable=False)
    calorias_totales = db.Column(db.Float, nullable=True)
    costo_produccion = db.Column(db.Float, nullable=True)
    rentabilidad = db.Column(db.Float, nullable=True)
