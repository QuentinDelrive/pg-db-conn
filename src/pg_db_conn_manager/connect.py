import os
from typing import overload
from collections.abc import Mapping
from functools import singledispatch

from pg_db_conn_manager import DBConnection

from ._types import ConnectionConfig
from ._const import DEFAULT_CONNECT, PGSQL_DEFAULT_PORT, PGSQL_DEFAULT_SSLMODE


@overload
def connect(
    host: str,
    password: str,
    user: str,
    database: str,
    port: int = 5432,
    sslmode: str = "require",
) -> DBConnection: ...


@overload
def connect(config: ConnectionConfig) -> DBConnection: ...


@overload
def connect() -> DBConnection: ...


@singledispatch
def connect(arg=None, *args) -> DBConnection:
    return connect(DEFAULT_CONNECT)


@connect.register(str)  # type: ignore
def _(
    host: str,
    password: str,
    user: str,
    database: str,
    port: int = PGSQL_DEFAULT_PORT,
    sslmode: str = PGSQL_DEFAULT_SSLMODE,
) -> DBConnection:
    return DBConnection(
        host=host,
        password=password,
        database=database,
        user=user,
        port=port,
        sslmode=sslmode,
    )


@connect.register(Mapping)  # type: ignore
def _(config: ConnectionConfig) -> DBConnection:
    return DBConnection(
        host=_resolve(config, "host"),  # type: ignore
        password=_resolve(config, "password"),  # type: ignore
        user=_resolve(config, "user"),  # type: ignore
        database=_resolve(config, "database"),  # type: ignore
        port=_resolve(config, "port", PGSQL_DEFAULT_PORT),  # type: ignore
        sslmode=_resolve(config, "sslmode", PGSQL_DEFAULT_SSLMODE),  # type: ignore
    )


def _resolve(
    config: ConnectionConfig, key: str, default: str | int | None = None
) -> str | int | None:
    val: str | int | None = config.get(key, default)  # type: ignore
    if isinstance(val, str) and val in os.environ:
        return os.getenv(val)
    return val
