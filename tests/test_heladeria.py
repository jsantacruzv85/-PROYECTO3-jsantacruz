import pytest
from app import app
from database import db
from models.ingrediente import Ingrediente
from models.producto import Producto

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Base de datos en memoria para pruebas
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_listar_ingredientes(client):
    # Crear datos de prueba
    ingrediente = Ingrediente(nombre="Leche", precio=1.5, calorias=50, inventario=100, es_vegetariano=True)
    db.session.add(ingrediente)
    db.session.commit()

    # Hacer la solicitud
    response = client.get('/api/heladeria/ingredientes')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['nombre'] == "Leche"

def test_vender_producto(client):
    # Crear datos de prueba
    producto = Producto(nombre="Chocolate", precio_publico=10, calorias_totales=200, costo_produccion=5, rentabilidad=0)
    ingrediente = Ingrediente(nombre="Cacao", precio=2, calorias=100, inventario=10, es_vegetariano=True)
    db.session.add(producto)
    db.session.add(ingrediente)
    db.session.commit()

    # Simular la venta
    response = client.post('/api/heladeria/productos/vender/1')
    assert response.status_code == 200
    assert response.json['message'] == "¡Producto Chocolate vendido exitosamente!"

def test_reabastecer_ingrediente(client):
    # Crear datos de prueba
    ingrediente = Ingrediente(nombre="Leche", precio=1.5, calorias=50, inventario=10, es_vegetariano=True)
    db.session.add(ingrediente)
    db.session.commit()

    # Reabastecer el ingrediente
    response = client.post('/api/heladeria/ingredientes/reabastecer/1', json={"cantidad": 20})
    assert response.status_code == 200
    assert response.json['message'] == "Inventario de Leche incrementado en 20 unidades"

    # Verificar el inventario actualizado
    ingrediente_actualizado = Ingrediente.query.get(1)
    assert ingrediente_actualizado.inventario == 30
