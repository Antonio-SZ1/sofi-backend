# Mini Sistema SOFIPO - Backend

Este proyecto es una implementación de un backend SOFIPO, siguiendo los requisitos de una Práctica Integral.

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
- `.env`: Archivo para variables de entorno (debes crearlo a partir de `.env.example`).

## Despliegue

**Pre-requisitos:**
- Docker
- Docker Compose

**Pasos:**

1.  **Clona el repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd sofipo-backend
    ```

2.  **Crea el archivo de entorno:**
    Copia el contenido del archivo `.env` proporcionado en la guía y guárdalo en la raíz del proyecto.

3.  **Haz ejecutable el script de la réplica:**
    ```bash
    chmod +x postgres-init/init-db.sh
    ```

4.  **Levanta todo el stack con Docker Compose:**
    ```bash
    docker compose up --build -d
    ```
    El comando `--build` fuerza la reconstrucción de las imágenes de tus aplicaciones. La `-d` lo ejecuta en modo detached (segundo plano).

5.  **Verifica que todo esté corriendo:**
    ```bash
    docker-compose ps
    ```
    Deberías ver todos los servicios con el estado `Up` o `running`.

## Uso de la API

La API estará disponible en `http://localhost:8000`. La documentación interactiva (Swagger UI) está en `http://localhost:8000/docs`.

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
export TOKEN="TU_ACCESS_TOKEN_AQUI"

curl -X POST "http://localhost:8000/api/v1/clients/" \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "full_name": "Juan Perez",
  "email": "juan.perez@example.com",
  "rfc": "PEPJ800101HNE"
}'
```

### 3. Consultar un Cliente (Endpoint Público)

```bash
curl -X GET "http://localhost:8000/api/v1/clients/PEPJ800101HNE"
```
La primera vez, tardará un poco más (consulta a la BD réplica). Las siguientes peticiones serán casi instantáneas (servidas desde Redis).

### 4. Crear un Préstamo (Endpoint Protegido)

Primero, obtén el `id` del cliente que creaste.

```bash
export CLIENT_ID="ID_DEL_CLIENTE_OBTENIDO"

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
export LOAN_ID="ID_DEL_PRESTAMO_OBTENIDO"

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

## Observabilidad (Opcional pero Recomendado)

Aunque no se implementó en este `docker-compose.yml` para mantener la simplicidad, el siguiente paso sería añadir servicios como:
- **OpenTelemetry Collector**: Para recibir trazas y métricas.
- **Jaeger**: Para visualizar trazas distribuidas. `http://localhost:16686`
- **Prometheus**: Para almacenar métricas. `http://localhost:9090`
- **Grafana**: Para visualizar métricas en dashboards. `http://localhost:3000`

Para integrarlos, deberías:
1.  Añadir los servicios al `docker-compose.yml`.
2.  Instalar las librerías de OpenTelemetry en las aplicaciones Python (`opentelemetry-distro`, `opentelemetry-exporter-otlp`).
3.  Instrumentar la aplicación FastAPI para que envíe datos al Collector.