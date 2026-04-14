from typing import Literal, TypedDict
from enum import Enum

from psycopg.sql import SQL


class FormatCopyVal(Enum):
    BIN = "(FORMAT BINARY)"
    CSV = "(FORMAT CSV)"
    NONE = ""


class OptionsCopy(TypedDict, total=False):
    format: Literal["csv", "text", "binary", ""]
    delimiter: str
    header: bool
    quote: str
    escape: str
    encoding: Literal["utf-8",]
    on_error: Literal["stop", "ignore"]


class CopyDir(Enum):
    FROMSTDIN = SQL(r"copy {table} {cols} from STDIN {with_statement};")
    TOSTDIN = SQL(r"copy {table} {cols} to STDOUT {with_statement};")
