set -e

rm -rf /var/lib/postgresql/data/*

until pg_isready -h postgres-primary -p 5432 -U "$POSTGRES_USER"
do
  echo "Waiting for primary node..."
  sleep 1s
done

pg_basebackup -h postgres-primary -p 5432 -U replica_user -D /var/lib/postgresql/data -Fp -Xs -P -R

chmod 0700 /var/lib/postgresql/data

exec postgres