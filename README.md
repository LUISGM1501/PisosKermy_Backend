# Backend - Sistema de Catálogo

Backend completo del sistema de catálogo de productos con autenticación JWT, gestión de categorías, etiquetas, proveedores y productos con paginación.

## Estructura del proyecto

```
.
├── docker-compose.yml           # PostgreSQL + API
├── Dockerfile
├── requirements.txt
├── run.py                       # Para desarrollo local sin Docker
├── create_first_admin.py        # Script para crear el primer admin
├── test_api.py                  # Script de pruebas de todas las APIs
└── app/
    ├── __init__.py              # Factory de la aplicación
    ├── config.py
    ├── database.py
    ├── models/                  # Modelos de base de datos
    ├── schemas/                 # Validación y serialización
    ├── repositories/            # Acceso a datos
    ├── services/                # Lógica de negocio
    ├── routes/                  # Endpoints HTTP
    └── utils/                   # Utilidades compartidas
```

## Instalación y ejecución

### Con Docker (recomendado)

```bash
# 1. Copiar .env.example a .env y editar las credenciales
cp .env.example .env

# 2. Levantar PostgreSQL y la API
docker compose up -d

# 3. Crear el primer admin
docker compose exec api python create_first_admin.py

# 4. Verificar que funciona
curl http://localhost:5000/health
```

### Sin Docker (desarrollo local)

```bash
# 1. Crear virtual environment
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Copiar .env.example a .env y ajustar DB_HOST=localhost
cp .env.example .env

# 4. Asegurarse de que PostgreSQL esté corriendo localmente

# 5. Ejecutar
python run.py

# 6. En otra terminal, crear el primer admin
python create_first_admin.py
```

## Pruebas

El script `test_api.py` verifica que todas las APIs funcionen correctamente:

```bash
# Con Docker
docker compose exec api python test_api.py

# Sin Docker (con la API corriendo)
python test_api.py
```

El script prueba:
- Health check
- Login y autenticación
- CRUD de categorías
- CRUD de etiquetas
- CRUD de proveedores
- CRUD de productos (con verificación de que el cliente no ve precios)
- Edición de contenido del sitio
- Lectura de la bitácora de auditoría

## APIs disponibles

### Públicas (sin autenticación)

- `GET /health` - Health check
- `GET /api/categories` - Listar categorías
- `GET /api/tags` - Listar etiquetas
- `GET /api/products?page=1&category_id=1&tag_id=2` - Listar productos (paginado, filtrado)
- `GET /api/site-content/{key}` - Obtener contenido del sitio (ej: about_us)
- `GET /uploads/{filename}` - Servir imágenes

### Admin (requieren token JWT en header `Authorization: Bearer <token>`)

**Auth:**
- `POST /api/auth/login` - Iniciar sesión
- `GET /api/auth/me` - Información del admin actual
- `GET /api/auth/audit` - Bitácora de auditoría (paginada)

**Categorías:**
- `GET /api/admin/categories`
- `POST /api/admin/categories`
- `PUT /api/admin/categories/{id}`
- `DELETE /api/admin/categories/{id}`

**Etiquetas:**
- `GET /api/admin/tags`
- `POST /api/admin/tags`
- `PUT /api/admin/tags/{id}`
- `DELETE /api/admin/tags/{id}`

**Proveedores:**
- `GET /api/admin/providers`
- `POST /api/admin/providers`
- `PUT /api/admin/providers/{id}`
- `DELETE /api/admin/providers/{id}`

**Productos:**
- `GET /api/admin/products?page=1` - Incluye precio y proveedores
- `POST /api/admin/products` - Soporta multipart/form-data para subir imagen
- `PUT /api/admin/products/{id}` - Soporta multipart/form-data para actualizar imagen
- `DELETE /api/admin/products/{id}`

**Contenido del sitio:**
- `PUT /api/admin/site-content/{key}` - Actualizar contenido (ej: about_us)

## Características clave

- **Separación de responsabilidades:** Modelo → Repository → Service → Route
- **Validación robusta:** Esquemas dedicados para validar entrada
- **Seguridad:** JWT con expiración de 8 horas, contraseñas hasheadas
- **Bitácora completa:** Todas las operaciones admin se registran con IP y detalles
- **Precio oculto al cliente:** Los productos públicos nunca incluyen precio ni proveedores
- **Paginación:** 15 productos por página
- **Filtrado:** Por categorías y etiquetas
- **Relaciones many-to-many:** Un producto puede tener varias categorías, etiquetas y proveedores
- **Subida de imágenes:** Almacenadas en `/uploads`, servidas por la API
