#!/bin/bash
set -e

create_database_and_user() {
    local db_name=$1
    local db_user=$2
    local db_password=$3
    
    echo "Creating database '$db_name' and user '$db_user'"
    
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
        DO \$\$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$db_user') THEN
                CREATE USER $db_user WITH PASSWORD '$db_password';
            END IF;
        END
        \$\$;
EOSQL

    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
        SELECT 'CREATE DATABASE $db_name OWNER $db_user'
        WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$db_name')\gexec
EOSQL

    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
        GRANT ALL PRIVILEGES ON DATABASE $db_name TO $db_user;
EOSQL

    echo "Database '$db_name' and user '$db_user' created successfully"
}

echo "Starting database initialization..."

create_database_and_user "connections_db" "connections_user" "connections_password"

echo "All databases initialized successfully!"
