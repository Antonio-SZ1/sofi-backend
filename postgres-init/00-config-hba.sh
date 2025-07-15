#!/bin/bash
# Este script se ejecuta en el postgres-primary para añadir las reglas de autenticación a pg_hba.conf.

echo "Añadiendo reglas de autenticación a pg_hba.conf..."

# Ruta al archivo pg_hba.conf principal dentro del contenedor
PG_HBA_CONF_PATH="$PGDATA/pg_hba.conf"

# Reglas de autenticación a añadir
# Usamos 'md5' para forzar la autenticación por contraseña, que es más segura.
# Asegúrate de que las contraseñas en tu .env coincidan con las de PostgreSQL.

# Regla para el usuario principal de la aplicación (sofipo_user)
# Permite conexiones desde cualquier IP en la red Docker con autenticación MD5.
APP_USER_HBA_RULE="host    all             ${POSTGRES_USER}      0.0.0.0/0               md5"

# Regla para el usuario de replicación (replica_user)
# Permite conexiones de replicación desde cualquier IP con autenticación MD5.
REPL_USER_HBA_RULE="host    replication     ${POSTGRES_REPLICA_USER}  0.0.0.0/0               md5"

# Añadir la regla para el usuario principal si no existe
if ! grep -qF "$APP_USER_HBA_RULE" "$PG_HBA_CONF_PATH"; then
  echo "$APP_USER_HBA_RULE" >> "$PG_HBA_CONF_PATH"
  echo "Regla para ${POSTGRES_USER} añadida a $PG_HBA_CONF_PATH."
else
  echo "La regla para ${POSTGRES_USER} ya existe en $PG_HBA_CONF_PATH."
fi

# Añadir la regla para el usuario de replicación si no existe
if ! grep -qF "$REPL_USER_HBA_RULE" "$PG_HBA_CONF_PATH"; then
  echo "$REPL_USER_HBA_RULE" >> "$PG_HBA_CONF_PATH"
  echo "Regla de replicación para ${POSTGRES_REPLICA_USER} añadida a $PG_HBA_CONF_PATH."
else
  echo "La regla de replicación para ${POSTGRES_REPLICA_USER} ya existe en $PG_HBA_CONF_PATH."
fi

echo "Configuración de pg_hba.conf completada."
