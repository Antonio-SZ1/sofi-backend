# Mini Sistema SOFIPO - Backend

Este proyecto es una implementación de un backend SOFIPO, siguiendo los requisitos de una practica Integral.

## Tecnologías Utilizadas

- **Lenguaje/Framework**: Python 3.11 con FastAPI
- **Base de Datos Relacional**: PostgreSQL 15 (con replicación primario-réplica)
- **ORM**: SQLAlchemy
- **Base de Datos Documental**: CouchDB 3.3
- **Mensajería Asíncrona**: RabbitMQ 3.11
- **Cache**: Redis 7
- **Seguridad**: JWT (JSON Web Tokens)
- **Orquestación**: Docker y Docker Compose

## Estructura

- `backend-api`: El microservicio principal que expone la API RESTful.
- `event-consumer`: Un servicio que escucha eventos de RabbitMQ y los almacena en CouchDB.
- `postgres-init`: Scripts para la inicialización y replicación de PostgreSQL.
- `docker-compose.yml`: Archivo orquestador de toda la infraestructura.
- `.env`: Archivo para variables de entorno.

## Despliegue

**Pre-requisitos:**
- Docker
- Docker Compose

**Pasos:**

1.  **Clona el repositorio:**
    ```bash
    git clone git@github.com:Antonio-SZ1/sofi-backend.git
    cd sofi-backend
    ```

2.  **Haz ejecutable el script inicial y el de la réplica:**
    ```bash
    chmod +x postgres-init/00-config-hba.sh
    chmod +x postgres-replica-config/init-db.sh
    chmod +x couchdb-init/setup-users-db.sh

    ```

3.  **Levanta todo el stack con Docker Compose:**
    ```bash
    docker compose up --build -d
    ```
    

4.  **Verifica que todo esté corriendo:**
    ```bash
    docker-compose ps
    ```
    Deberías ver todos los servicios con el estado `Up` o `running`.

## Uso de la API

La API estará disponible en `http://localhost:8000`. La documentación interactiva está en `http://localhost:8000/docs`.

### 1. Obtener un Token de Autenticación

Para usar los endpoints protegidos (POST, PUT, DELETE), primero necesitas un token.

```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=admin&password=string"
```

**Respuesta:**
```json
{
  "access_token": "ey...",
  "token_type": "bearer"
}
```
Copia el valor de `access_token` para las siguientes peticiones.

### 2. Crear un Cliente (Endpoint Protegido)

```bash
export TOKEN="Tu token de acceso"

curl -X POST "http://localhost:8000/api/v1/clients/" \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "full_name": "Carlos Perez",
  "email": "carlos.perez@example.com",
  "rfc": "PEPJ800101HNE"
}'
```

### 3. Consultar un Cliente (Endpoint Público)

```bash
curl -X GET "http://localhost:8000/api/v1/clients/PEPJ800101HNE"
```
La primera vez, tardará un poco más . Las siguientes peticiones serán casi instantáneas (servidas desde Redis).

### 4. Crear un Préstamo (Endpoint Protegido)

Primero, obtén el `id` del cliente que creaste.

```bash
export CLIENT_ID="ID del cliente"

curl -X POST "http://localhost:8000/api/v1/loans/" \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "client_id": "'$CLIENT_ID'",
  "amount": 50000.00,
  "interest_rate": 0.15,
  "term_months": 24
}'
```

### 5. Registrar un Pago (Endpoint Protegido)

Obtén el `id` del préstamo.

```bash
export LOAN_ID="ID del prestamo"

curl -X POST "http://localhost:8000/api/v1/loans/$LOAN_ID/payments" \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "amount": 2500.00
}'
```

## Verificación de Flujos

- **Logs de la API y Consumidor**:
  ```bash
  docker-compose logs -f backend-api
  docker-compose logs -f event-consumer
  ```
- **RabbitMQ Management UI**: Ve a `http://localhost:15672` (user: `guest`, pass: `guest`). Podrás ver el exchange `sofipo_events_exchange` y la cola `couchdb_event_log_queue`.
- **CouchDB Fauxton UI**: Ve a `http://localhost:5984/_utils/` (user: `admin`, pass: `password`). Busca la base de datos `business_events` para ver todos los documentos JSON generados por el consumidor.
