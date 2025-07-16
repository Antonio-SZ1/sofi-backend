set -e

COUCHDB_URL="http://localhost:5984"
ADMIN_USER="${COUCHDB_USER}"
ADMIN_PASSWORD="${COUCHDB_PASSWORD}"

echo "--- Iniciando script setup-users-db.sh para CouchDB ---"

echo "Esperando a que el servicio HTTP de CouchDB esté completamente listo..."

MAX_ATTEMPTS=60 
ATTEMPT_INTERVAL=2

for i in $(seq 1 $MAX_ATTEMPTS); do

  if curl -s -f -u "$ADMIN_USER:$ADMIN_PASSWORD" "$COUCHDB_URL" > /dev/null; then
    echo "CouchDB está listo y accesible (intento $i/$MAX_ATTEMPTS)."
    break
  else
    echo "CouchDB no está listo (intento $i/$MAX_ATTEMPTS). Reintentando en $ATTEMPT_INTERVAL segundos..."
    sleep $ATTEMPT_INTERVAL
  fi

  if [ $i -eq $MAX_ATTEMPTS ]; then
    echo "Error: CouchDB no respondió después de $MAX_ATTEMPTS intentos. Abortando configuración."
    exit 1
  fi
done

echo "CouchDB listo. Procediendo con la configuración de usuarios y bases de datos."

DB_NAME="my_app_db"
echo "Creando base de datos '$DB_NAME' si no existe..."
response=$(curl -s -u "$ADMIN_USER:$ADMIN_PASSWORD" -X PUT "$COUCHDB_URL/$DB_NAME" -H "Content-Type: application/json")

if echo "$response" | grep -q '"ok":true'; then
  echo "Base de datos '$DB_NAME' creada exitosamente."
elif echo "$response" | grep -q '"error":"file_exists"'; then
  echo "Base de datos '$DB_APP_DB' ya existe."
else
  echo "Error al crear la base de datos '$DB_NAME'. Respuesta: $response"
  exit 1 
fi

echo "Configuración inicial de CouchDB completada."
