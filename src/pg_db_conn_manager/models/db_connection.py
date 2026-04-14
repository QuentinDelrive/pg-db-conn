from contextlib import contextmanager
from types import TracebackType
from typing import LiteralString, NoReturn, Optional, cast
import logging

import psycopg as pg
from psycopg import sql
from psycopg.connection import Connection
from psycopg.cursor import Cursor
from psycopg.sql import SQL, Composable

from .._errors import ConnectionNotInitialized
from .._types import FormatCopyVal, OptionsCopy, CopyDir

logger = logging.getLogger()


class DBConnection:
    def __init__(
        self,
        host: str,
        database: str,
        user: str,
        password: str,
        port: int = 5432,
        sslmode: str = "require",
    ) -> None:
        self.host: str = host
        self.database: str = database
        self.user: str = user
        self.password: str = password
        self.port: int = port
        self.sslmode: str = sslmode
        self._conn: Connection | None = None
        self._conn_setup = False
        logger.debug("Init successful")

    def cursor(self) -> Cursor:
        if not self._conn_setup:
            msg = "Can't get a cursor from a non initialized connection."
            self._raise_not_init(msg)
        return self._conn.cursor()  # type: ignore

    @contextmanager
    def copy(
        self,
        base_query: CopyDir,
        target: str,
        cols: list[str] = [],
        copy_format: FormatCopyVal = FormatCopyVal.NONE,
        options: Optional[OptionsCopy] = None,
    ):
        if not self._conn_setup:
            msg = "Can't copy from a non existing connection"
            self._raise_not_init(msg)
        if cols:
            cols_str = "("
            cols_str += cast(LiteralString, ", ".join(cols))
            cols_str += ")"
        else:
            cols_str = ""

        if "select" in target.lower():
            table = SQL(f"({target})")  # type:ignore
        else:
            table_parts = target.split(".")
            table = sql.Identifier(*table_parts)

        params = []
        if options:
            parts = []
            for k, v in options.items():
                parts.append(sql.SQL(f"{k} %s"))  # type: ignore
                params.append(v)

            with_statement = SQL(" WITH ({}").format(SQL(", ").join(parts)) + SQL(")")
        else:
            with_statement = SQL("")

        query: Composable = base_query.value.format(
            table=table,
            cols=SQL(cols_str),
            binar=sql.SQL(copy_format.value),
            with_statement=with_statement,
        )
        with self.cursor() as cur:
            with cur.copy(query, params) as copy:
                yield copy

    def execute(self, query: SQL, params: tuple | dict | None = None):
        with self.cursor() as cur:
            cur.execute(query, params)  # type: ignore

    def commit(self) -> None:
        if self._conn_setup:
            self._conn.commit()  # type: ignore
            return
        msg = "Can't commit non initialized connection"
        self._raise_not_init(msg)

    def rollback(self) -> None:
        if self._conn_setup:
            self._conn.rollback()  # type: ignore
            return
        msg = "Can't rollback non initialized connection"
        self._raise_not_init(msg)

    def open(self) -> None:
        self._conn = pg.connect(
            dbname=self.database,
            host=self.host,
            user=self.user,
            password=self.password,
            port=self.port,
            sslmode=self.sslmode,
        )
        logger.debug("load connection to db successful")
        self._conn_setup = True
        logger.debug("_conn_setup set to True")

    def close(self):
        if not self._conn_setup:
            msg = "Can't close a non initialized connection"
            self._raise_not_init(msg)
        self._conn.close()  # type:ignore
        logger.debug("connection closed")
        self._conn_setup = False
        logger.debug("_conn_setup set to False")

    def _raise_not_init(self, msg: str) -> NoReturn:
        logger.error(msg)
        raise ConnectionNotInitialized(msg)

    def __enter__(self) -> "DBConnection":
        self.open()
        return self

    def __exit__(
        self,
        exc_type: type | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._conn_setup:
            if exc_type is None:
                self.commit()  # type: ignore
            else:
                self._conn.rollback()  # type: ignore
            self.close()
