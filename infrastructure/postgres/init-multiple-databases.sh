#!/bin/bash
set -e

PGHOST=${PGHOST:-localhost}
PGPORT=${PGPORT:-5432}
PGPASSWORD=${POSTGRES_PASSWORD}

export PGPASSWORD

echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h "$PGHOST" -p "$PGPORT" -U "$POSTGRES_USER" > /dev/null 2>&1; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
done
echo "PostgreSQL is ready!"

create_database_and_user() {
    local db_name=$1
    local db_user=$2
    local db_password=$3
    
    echo "Creating database '$db_name' and user '$db_user'"
    
    psql -v ON_ERROR_STOP=1 -h "$PGHOST" -p "$PGPORT" --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
        DO \$\$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$db_user') THEN
                CREATE USER $db_user WITH PASSWORD '$db_password';
            END IF;
        END
        \$\$;
EOSQL

    psql -v ON_ERROR_STOP=1 -h "$PGHOST" -p "$PGPORT" --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
        SELECT 'CREATE DATABASE $db_name OWNER $db_user'
        WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$db_name')\gexec
EOSQL

    psql -v ON_ERROR_STOP=1 -h "$PGHOST" -p "$PGPORT" --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
        GRANT ALL PRIVILEGES ON DATABASE $db_name TO $db_user;
EOSQL

    echo "Database '$db_name' and user '$db_user' created successfully"
}

echo "Starting database initialization..."

create_database_and_user \
  "${POSTGRES_CONNECTIONS_DB:-connections_db}" \
  "${POSTGRES_CONNECTIONS_USER:-connections_user}" \
  "${POSTGRES_CONNECTIONS_PASSWORD:-connections_password}"

create_database_and_user \
  "${POSTGRES_MODULES_DB:-modules_db}" \
  "${POSTGRES_MODULES_USER:-modules_user}" \
  "${POSTGRES_MODULES_PASSWORD:-modules_password}"

create_database_and_user \
  "${POSTGRES_PROJECTS_DB:-projects_db}" \
  "${POSTGRES_PROJECTS_USER:-projects_user}" \
  "${POSTGRES_PROJECTS_PASSWORD:-projects_password}"

create_database_and_user \
  "${POSTGRES_BOT_DB:-bot_db}" \
  "${POSTGRES_BOT_USER:-bot_user}" \
  "${POSTGRES_BOT_PASSWORD:-bot_password}"

echo "All databases initialized successfully!"
