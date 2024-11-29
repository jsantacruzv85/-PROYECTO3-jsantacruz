from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models.ingrediente import Ingrediente
from models.producto import Producto
from models.usuario import Usuario, UserMixin
from database import db
from controllers.auth_controller import token_required, role_required_api, role_required_html

heladeria_bp = Blueprint('heladeria', __name__, url_prefix='/heladeria')


# *** RUTAS DEL FRONTEND ***

# Página de inicio para listar productos
@heladeria_bp.route('/productos', methods=['GET'])
def pagina_listar_productos():
    """
    Página de inicio para listar productos.
    Accesible por cualquier usuario (incluso no autenticado).
    """
    productos = Producto.query.all()
    return render_template('productos.html', productos=productos)

# Página para detalles de un producto
@heladeria_bp.route('/productos/detalle/<int:id>', methods=['GET'])
def pagina_detalle_producto(id):
    """
    Muestra los detalles de un producto específico.
    """
    producto = Producto.query.get(id)
    if not producto:
        flash('Producto no encontrado.', 'error')
        return redirect(url_for('heladeria.pagina_listar_productos'))

    # Filtrar campos sensibles según el rol del usuario
    detalles_producto = {
        'id': producto.id,
        'nombre': producto.nombre,
        'precio_publico': producto.precio_publico,
        'calorias_totales': producto.calorias_totales
    }

    if current_user.is_authenticated and current_user.es_admin:
        detalles_producto.update({
            'costo_produccion': producto.costo_produccion,
            'rentabilidad': producto.rentabilidad
        })

    return render_template('detalle_producto.html', producto=detalles_producto)


# Página para listar ingredientes
@heladeria_bp.route('/ingredientes', methods=['GET'])
@login_required
@role_required_html('empleado', 'admin') # Permite tanto a empleados como administradores
def pagina_listar_ingredientes():
    """
    Lista todos los ingredientes.
    Solo accesible por empleados y administradores.
    """
    ingredientes = Ingrediente.query.all()
    return render_template('ingredientes.html', ingredientes=ingredientes)

# Página para reabastecer ingredientes
@heladeria_bp.route('/ingredientes/reabastecer/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required_html('admin')
def pagina_reabastecer_ingrediente(id):
    """
    Permite reabastecer el inventario de un ingrediente específico.
    Solo accesible por administradores.
    """
    ingrediente = Ingrediente.query.get(id)
    if not ingrediente:
        flash('Ingrediente no encontrado.', 'error')
        return redirect(url_for('heladeria.pagina_listar_ingredientes'))

    if request.method == 'POST':
        cantidad = int(request.form.get('cantidad', 0))
        ingrediente.inventario += cantidad
        db.session.commit()
        flash(f'Inventario de {ingrediente.nombre} incrementado en {cantidad} unidades.', 'success')
        return redirect(url_for('heladeria.pagina_listar_ingredientes'))

    return render_template('reabastecer_ingrediente.html', ingrediente=ingrediente)

# Página para vender un producto
@heladeria_bp.route('/productos/vender/<int:id>', methods=['GET', 'POST'])
def pagina_vender_producto(id):
    """
    Permite vender un producto.
    Accesible por cualquier usuario autenticado.
    """
    producto = Producto.query.get(id)
    if not producto:
        flash('Producto no encontrado.', 'error')
        return redirect(url_for('heladeria.pagina_listar_productos'))

    if request.method == 'POST':
        # Simular venta
        producto.rentabilidad += producto.precio_publico
        db.session.commit()
        flash(f'Producto {producto.nombre} vendido exitosamente.', 'success')
        return redirect(url_for('heladeria.pagina_listar_productos'))

    return render_template('vender_producto.html', producto=producto)

# Página para renovar inventario de un producto
@heladeria_bp.route('/productos/renovar/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required_html('admin')
def pagina_renovar_inventario_producto(id):
    """
    Permite renovar el inventario de un producto.
    Solo accesible por administradores.
    """
    producto = Producto.query.get(id)
    if not producto:
        flash('Producto no encontrado.', 'error')
        return redirect(url_for('heladeria.pagina_listar_productos'))

    if request.method == 'POST':
        nueva_cantidad = int(request.form.get('nueva_cantidad', 0))
        producto.inventario = nueva_cantidad
        db.session.commit()
        flash(f'Inventario del producto {producto.nombre} renovado a {nueva_cantidad} unidades.', 'success')
        return redirect(url_for('heladeria.pagina_listar_productos'))

    return render_template('renovar_inventario.html', producto=producto)


# *** RUTAS API REST ***

# Crear un administrador
@heladeria_bp.route('/usuarios/crear_admin', methods=['POST'])
@token_required
@role_required_api('admin')
def crear_admin(current_user):
    """
    Crear un usuario administrador.
    Acceso: Solo administrador.
    """
    if Usuario.query.filter_by(username="admin").first():
        return jsonify({"error": "El usuario admin ya existe"}), 400

    nuevo_usuario = Usuario(username="admin", password="admin123", es_admin=True)
    db.session.add(nuevo_usuario)
    db.session.commit()
    return jsonify({"message": "Usuario admin creado exitosamente."})

# Listar todos los productos (Acceso público)
@heladeria_bp.route('/api/productos', methods=['GET'])
def listar_productos():
    """
    Listar todos los productos.
    Acceso: Público (no requiere autenticación).
    """
    productos = Producto.query.all()

    productos_data = []
    for producto in productos:
        # Datos básicos visibles para todos
        producto_info = {
            'id': producto.id,
            'nombre': producto.nombre,
            'precio_publico': producto.precio_publico,
            'calorias_totales': producto.calorias_totales
        }

        # Solo el administrador puede ver el costo y la rentabilidad
        if current_user.is_authenticated and current_user.es_admin:
            producto_info.update({
                'costo_produccion': producto.costo_produccion,
                'rentabilidad': producto.rentabilidad
            })

        productos_data.append(producto_info)

    return jsonify(productos_data), 200


# Consultar un producto por ID (Clientes, empleados, administradores)
@heladeria_bp.route('/api/productos/<int:id>', methods=['GET'])
@token_required
@role_required_api('admin', 'empleado', 'cliente')
def obtener_producto(current_user, id):
    """
    Consultar un producto por ID.
    """
    print(current_user.__dict__)  # Depuración para verificar roles y datos
    producto = Producto.query.get(id)
    if not producto:
        return jsonify({'error': 'Producto no encontrado'}), 404
    return jsonify({
        'id': producto.id,
        'nombre': producto.nombre,
        'precio_publico': producto.precio_publico,
        'calorias_totales': producto.calorias_totales,
        'costo_produccion': producto.costo_produccion,
        'rentabilidad': producto.rentabilidad
    })


# Consultar un producto según su nombre
@heladeria_bp.route('/api/productos/nombre/<string:nombre>', methods=['GET'])
@token_required
@role_required_api('empleado', 'admin')
def obtener_producto_por_nombre(current_user, nombre):
    """
    Consultar un producto según su nombre.
    Acceso: Empleados y administradores.
    """
    producto = Producto.query.filter_by(nombre=nombre).first()
    if not producto:
        return jsonify({'error': 'Producto no encontrado'}), 404
    return jsonify({
        'id': producto.id,
        'nombre': producto.nombre,
        'precio_publico': producto.precio_publico,
        'calorias_totales': producto.calorias_totales,
        'costo_produccion': producto.costo_produccion,
        'rentabilidad': producto.rentabilidad
    })

# Consultar un ingrediente según su nombre
@heladeria_bp.route('/api/ingredientes/nombre/<string:nombre>', methods=['GET'])
@token_required
@role_required_api('empleado', 'admin')
def obtener_ingrediente_por_nombre(current_user, nombre):
    """
    Consultar un ingrediente según su nombre.
    Acceso: Empleados y administradores.
    """
    ingrediente = Ingrediente.query.filter_by(nombre=nombre).first()
    if not ingrediente:
        return jsonify({'error': 'Ingrediente no encontrado'}), 404
    return jsonify({
        'id': ingrediente.id,
        'nombre': ingrediente.nombre,
        'precio': ingrediente.precio,
        'calorias': ingrediente.calorias,
        'inventario': ingrediente.inventario,
        'es_vegetariano': ingrediente.es_vegetariano
    })

# Reabastecer un producto según su ID
@heladeria_bp.route('/api/productos/reabastecer/<int:id>', methods=['POST'])
@token_required
@role_required_api('empleado', 'admin')
def reabastecer_producto(current_user, id):
    """
    Reabastecer un producto por ID.
    Acceso: Empleados y administradores.
    """
    data = request.get_json()
    cantidad = data.get('cantidad', 0)

    producto = Producto.query.get(id)
    if not producto:
        return jsonify({'error': 'Producto no encontrado'}), 404

    producto.inventario += cantidad
    db.session.commit()
    return jsonify({'message': f'Inventario de {producto.nombre} incrementado en {cantidad} unidades'})


# Consultar calorías de un producto (Clientes, empleados, administradores)
@heladeria_bp.route('/api/productos/<int:id>/calorias', methods=['GET'])
@token_required
@role_required_api('cliente', 'empleado', 'admin')
def consultar_calorias(current_user, id):
    """
    Consultar las calorías de un producto.
    Acceso: Clientes, empleados y administradores.
    """
    producto = Producto.query.get(id)
    if not producto:
        return jsonify({'error': 'Producto no encontrado'}), 404
    return jsonify({'calorias_totales': producto.calorias_totales})

# Consultar rentabilidad de un producto (Solo administradores)
@heladeria_bp.route('/api/productos/<int:id>/rentabilidad', methods=['GET'])
@token_required
@role_required_api('admin')
def consultar_rentabilidad(current_user, id):
    """
    Consultar la rentabilidad de un producto.
    Acceso: Solo administradores.
    """
    producto = Producto.query.get(id)
    if not producto:
        return jsonify({'error': 'Producto no encontrado'}), 404
    return jsonify({'rentabilidad': producto.rentabilidad})

# Consultar el costo de producción de un producto (administradores)
@heladeria_bp.route('/api/productos/<int:id>/costo_produccion', methods=['GET'])
@token_required
@role_required_api('admin')
def consultar_costo_produccion(current_user, id):
    """
    Consultar el costo de producción de un producto.
    Acceso: administradores.
    """
    producto = Producto.query.get(id)
    if not producto:
        return jsonify({'error': 'Producto no encontrado'}), 404
    return jsonify({'costo_produccion': producto.costo_produccion})

# Vender un producto por ID (Clientes, empleados, administradores)
@heladeria_bp.route('/api/productos/vender/<int:id>', methods=['POST'])
@token_required
@role_required_api('cliente', 'empleado', 'admin')
def vender_producto(current_user, id):
    """
    Vender un producto por ID.
    Acceso: Clientes, empleados y administradores.
    """
    producto = Producto.query.get(id)
    if not producto:
        return jsonify({'error': 'Producto no encontrado'}), 404
    # Registrar venta
    producto.rentabilidad += producto.precio_publico
    db.session.commit()
    return jsonify({'message': f'¡Producto {producto.nombre} vendido exitosamente!'})

# Listar todos los ingredientes (Empleados y administradores)
@heladeria_bp.route('/api/ingredientes', methods=['GET'])
@token_required
@role_required_api('empleado', 'admin')
def listar_ingredientes(current_user):
    """
    Listar todos los ingredientes.
    Acceso: Empleados y administradores.
    """
    ingredientes = Ingrediente.query.all()
    return jsonify([{
        'id': i.id,
        'nombre': i.nombre,
        'precio': i.precio,
        'calorias': i.calorias,
        'inventario': i.inventario,
        'es_vegetariano': i.es_vegetariano
    } for i in ingredientes])

# Consultar un ingrediente por ID (Empleados y administradores)
@heladeria_bp.route('/api/ingredientes/<int:id>', methods=['GET'])
@token_required
@role_required_api('empleado', 'admin')
def obtener_ingrediente_por_id(current_user, id):
    """
    Consultar un ingrediente por ID.
    Acceso: Empleados y administradores.
    """
    ingrediente = Ingrediente.query.get(id)
    if not ingrediente:
        return jsonify({'error': 'Ingrediente no encontrado'}), 404
    return jsonify({
        'id': ingrediente.id,
        'nombre': ingrediente.nombre,
        'precio': ingrediente.precio,
        'calorias': ingrediente.calorias,
        'inventario': ingrediente.inventario,
        'es_vegetariano': ingrediente.es_vegetariano
    })

# Consultar si un ingrediente es sano (Clientes, empleados, administradores)
@heladeria_bp.route('/api/ingredientes/<int:id>/es_sano', methods=['GET'])
@token_required
@role_required_api('cliente', 'empleado', 'admin')
def consultar_ingrediente_es_sano(current_user, id):
    """
    Consultar si un ingrediente es sano según su ID.
    Acceso: Clientes, empleados y administradores.
    """
    ingrediente = Ingrediente.query.get(id)
    if not ingrediente:
        return jsonify({'error': 'Ingrediente no encontrado'}), 404
    es_sano = ingrediente.calorias < 100 and ingrediente.es_vegetariano
    return jsonify({'id': ingrediente.id, 'nombre': ingrediente.nombre, 'es_sano': es_sano})

# Reabastecer un ingrediente (Empleados y administradores)
@heladeria_bp.route('/api/ingredientes/reabastecer/<int:id>', methods=['POST'])
@token_required
@role_required_api('empleado', 'admin')
def reabastecer_ingrediente(current_user, id):
    """
    Reabastecer un ingrediente por ID.
    Acceso: Empleados y administradores.
    """
    data = request.get_json()
    cantidad = data.get('cantidad', 0)

    ingrediente = Ingrediente.query.get(id)
    if not ingrediente:
        return jsonify({'error': 'Ingrediente no encontrado'}), 404

    ingrediente.inventario += cantidad
    db.session.commit()
    return jsonify({'message': f'Inventario de {ingrediente.nombre} incrementado en {cantidad} unidades'})

# Renovar inventario de un producto por ID
@heladeria_bp.route('/api/productos/renovar/<int:id>', methods=['POST'])
@token_required
@role_required_api('admin')  # Solo accesible para administradores
def renovar_inventario_producto(current_user, id):
    """
    Actualiza el inventario de un producto según su ID.
    Solo accesible por administradores.
    """
    # Buscar el producto por ID
    producto = Producto.query.get(id)
    if not producto:
        return jsonify({'error': 'Producto no encontrado'}), 404

    # Obtener nueva cantidad del cuerpo de la solicitud
    data = request.get_json()
    nueva_cantidad = data.get('nueva_cantidad', None)
    
    if nueva_cantidad is None or not isinstance(nueva_cantidad, int) or nueva_cantidad < 0:
        return jsonify({'error': 'La nueva cantidad debe ser un número entero positivo'}), 400

    # Actualizar el inventario del producto
    producto.inventario = nueva_cantidad
    db.session.commit()

    return jsonify({'message': f'Inventario del producto "{producto.nombre}" renovado a {nueva_cantidad} unidades'})



# *** MÉTODOS AUXILIARES ***

def manejar_no_autorizado(e):
    """
    Renderiza la página de error 403.
    """
    return render_template('403.html'), 403

# Agregar el manejador de errores
heladeria_bp.app_errorhandler(403)(manejar_no_autorizado)
