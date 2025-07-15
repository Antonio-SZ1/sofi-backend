#!/bin/bash
set -e

COUCHDB_URL="http://localhost:5984"
ADMIN_USER="${COUCHDB_USER}"
ADMIN_PASSWORD="${COUCHDB_PASSWORD}"

echo "--- Iniciando script setup-users-db.sh para CouchDB ---"

echo "Esperando a que el servicio HTTP de CouchDB esté completamente listo..."

MAX_ATTEMPTS=60 # Intentar por 60 * 2 = 120 segundos (2 minutos)
ATTEMPT_INTERVAL=2 # Esperar 2 segundos entre intentos

for i in $(seq 1 $MAX_ATTEMPTS); do
  # Intentar una petición GET simple a la raíz de CouchDB
  # -s: Silent mode. -f: Fail silently (no output on HTTP errors).
  # -u: User and password for server authentication.
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

# Crear base de datos de ejemplo si no existe
DB_NAME="my_app_db"
echo "Creando base de datos '$DB_NAME' si no existe..."
response=$(curl -s -u "$ADMIN_USER:$ADMIN_PASSWORD" -X PUT "$COUCHDB_URL/$DB_NAME" -H "Content-Type: application/json")

if echo "$response" | grep -q '"ok":true'; then
  echo "Base de datos '$DB_NAME' creada exitosamente."
elif echo "$response" | grep -q '"error":"file_exists"'; then
  echo "Base de datos '$DB_APP_DB' ya existe."
else
  echo "Error al crear la base de datos '$DB_NAME'. Respuesta: $response"
  exit 1 # Salir con error si la creación de la DB falla
fi

echo "Configuración inicial de CouchDB completada."
