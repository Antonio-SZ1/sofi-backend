set -e

echo "--- Iniciando script init-db.sh para postgres-replica ---"

echo "Limpiando directorio de datos de la réplica: /var/lib/postgresql/data"
rm -rf /var/lib/postgresql/data/*
mkdir -p /var/lib/postgresql/data
chmod 0700 /var/lib/postgresql/data
echo "Directorio de datos limpio y permisos establecidos."

echo "Esperando a que el nodo primario (postgres-primary:5432) esté listo..."
until PGPASSWORD="${POSTGRES_PASSWORD}" pg_isready -h postgres-primary -p 5432 -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" > /dev/null 2>&1
do
  echo "El primario no está listo o la conexión falló. Reintentando en 1 segundo..."
  sleep 1
done
echo "El nodo primario está listo y accesible."

echo "Iniciando pg_basebackup para la replicación..."
echo "Usuario de replicación: ${POSTGRES_REPLICA_USER}"
echo "Host primario: postgres-primary"

export PGPASSWORD="${POSTGRES_REPLICA_PASSWORD}"

if pg_basebackup -h postgres-primary -p 5432 -U "${POSTGRES_REPLICA_USER}" -D /var/lib/postgresql/data -Fp -Xs -P -R; then
  echo "pg_basebackup completado exitosamente."
else
  echo "Error: pg_basebackup falló. Revisar logs anteriores para detalles."
  exit 1 
fi

unset PGPASSWORD

echo "Llamando al entrypoint original de PostgreSQL para iniciar el servidor como réplica..."

exec /usr/local/bin/docker-entrypoint.sh postgres -c hot_standby=on -c hot_standby_feedback=on
