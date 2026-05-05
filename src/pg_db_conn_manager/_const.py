from pg_db_conn_manager._types import ConnectionConfig


PGSQL_DEFAULT_PORT = 5432
PGSQL_DEFAULT_SSLMODE = "require"


DEFAULT_CONNECT: ConnectionConfig = {
    "host": "PGHOST",
    "password": "PGPASSWORD",
    "user": "PGUSER",
    "port": "PGPORT",
    "sslmode": "PGSSLMODE",
    "database": "PGDATABASE",
}
