from database import db

class Ingrediente(db.Model):
    __tablename__ = 'ingredientes'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    calorias = db.Column(db.Float, nullable=False)
    inventario = db.Column(db.Integer, default=0)
    es_vegetariano = db.Column(db.Boolean, default=False)

    def es_sano(self):
        return self.calorias < 100 or self.es_vegetariano
