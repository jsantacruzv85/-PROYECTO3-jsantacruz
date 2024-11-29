# Heladería

Una API desarrollada para la gestión eficiente de una heladería. Este proyecto incluye autenticación, gestión de productos, ingredientes y usuarios, con evidencias de pruebas completas realizadas en Postman.

---

## **Requisitos**

Antes de empezar, asegúrate de tener instalado:
- [Python 3.10+](https://www.python.org/downloads/)
- [MySQL Server](https://dev.mysql.com/downloads/mysql/)
- [Virtualenv](https://pypi.org/project/virtualenv/)

---

## **Instalación y configuración**

### **1. Clonar el repositorio**
```bash
git clone https://github.com/tu_usuario/heladeria.git
cd heladeria
```
### **2. Crear un entorno virtual e instalar dependencias**
```bash
python -m venv venv
source venv/bin/activate   # En Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```
### **3. Configurar el entorno**
Crea un archivo .env en la raíz del proyecto basado en .env.example y completa los valores necesarios:
```env
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=3306
DB_NAME=heladeria
SECRET_KEY=clave_secreta_segura
```
### **4. Configurar la base de datos**
Asegúrate de que tu servidor MySQL esté en ejecución. Luego, ejecuta el siguiente comando para poblar la base de datos:
```bash
python poblar_base_datos.py
```
## **Ejecución de la aplicación**
Para iniciar el servidor de desarrollo, usa:
```bash
python app.py
```
Accede a la aplicación en tu navegador en: http://127.0.0.1:5000
## **Estructura del proyecto**
```graphql
heladeria/
│
├── app.py                   # Archivo principal para ejecutar la aplicación
├── poblar_base_datos.py     # Script para poblar la base de datos
├── .env.example             # Archivo de ejemplo para configuración del entorno
│
├── controllers/             # Lógica de negocio y controladores
│   ├── auth_controller.py       # Controlador de autenticación
│   └── heladeria_controller.py  # Controlador principal de la heladería
│
├── models/                  # Definición de modelos de la base de datos
│   ├── usuario.py
│   ├── producto.py
│   └── ingrediente.py
│
├── static/                  # Archivos estáticos (CSS, JS)
├── templates/               # Plantillas HTML para el frontend
├── requirements.txt         # Dependencias del proyecto
├── Documentacion_Api_Rest/  # Carpeta para almacenar documentos de la API REST
│   ├── Documentación_API_REST_Heladería.docx  # Detalles técnicos de la API
│   └── Evidencias_API_REST.docx              # Evidencias del desarrollo y pruebas
└── README.md                # Archivo con información general del proyecto
```
## **Documentación de Endpoints**
Consulta la documentación completa en el archivo: Documentación del API REST de la Heladería.docx.

Ejemplo de endpoints disponibles:
### **Autenticación** ###
- **Login para API:** POST /auth/api_login
- **Registrar usuarios:** POST /auth/register
### **Productos** ###
- **Consultar todos los productos:** GET /heladeria/api/productos
- **Vender un producto:** POST /heladeria/api/productos/vender/<id>
### **Ingredientes**
- **Consultar todos los ingredientes:** GET /heladeria/api/ingredientes
- **Reabastecer un ingrediente:** POST /heladeria/api/ingredientes/reabastecer/<id>

## **Pruebas**
Se realizaron pruebas exhaustivas en Postman. Las evidencias de estas pruebas están documentadas en:

    - EVIDENCIAS API Rest.docx



