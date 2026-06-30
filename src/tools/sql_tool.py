"""
Feature 3 - SQL validation + execution.
Validation is the safety boundary: any write keyword, multi-statement
injection, or non-SELECT/WITH query is rejected before it ever touches
the database. The connection itself is also opened read-only as
defense-in-depth.
"""
import os
import re
import sqlite3

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DB_PATH = os.path.join(_BASE_DIR, "data", "database.db")

_BLOCKED_KEYWORDS = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]


class SQLValidationError(Exception):
    pass


def validate_sql(query: str) -> None:
    """Raises SQLValidationError if the query is not safe read-only SQL."""
    stripped = query.strip().rstrip(";")

    if ";" in stripped:
        raise SQLValidationError("Multiple statements are not allowed.")

    upper = stripped.upper()
    if not (upper.startswith("SELECT") or upper.startswith("WITH")):
        raise SQLValidationError("Only SELECT/WITH (read-only) queries are allowed.")

    for keyword in _BLOCKED_KEYWORDS:
        if re.search(rf"\b{keyword}\b", upper):
            raise SQLValidationError(f"Query contains a blocked keyword: {keyword}")


def execute_sql(query: str) -> list[dict]:
    """
    Validates then executes the query against the read-only DB connection.
    Raises SQLValidationError for unsafe queries, sqlite3.Error for
    syntax errors - callers must catch both and explain to the user.
    """
    validate_sql(query)

    uri_path = f"file:{_DB_PATH}?mode=ro"
    conn = sqlite3.connect(uri_path, uri=True)
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
