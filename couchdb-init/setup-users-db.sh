

echo "Esperando a que CouchDB esté listo..."
until curl -s http://localhost:5984/_up -o /dev/null; do
  sleep 1
done
echo "CouchDB está listo."


COUCHDB_USER="${COUCHDB_USER}"
COUCHDB_PASSWORD="${COUCHDB_ADMIN_PASSWORD}" 

echo "Intentando crear la base de datos _users..."
response=$(curl -s -X PUT "http://${COUCHDB_USER}:${COUCHDB_PASSWORD}@localhost:5984/_users" -H "Content-Type: application/json" -d '{}')

if echo "$response" | grep -q "file_exists"; then
  echo "La base de datos _users ya existe. Continuando."
elif echo "$response" | grep -q "ok"; then
  echo "Base de datos _users creada exitosamente."
else
  echo "Error al crear la base de datos _users:"
  echo "$response"
  exit 1
fi

echo "Inicialización de CouchDB completada."