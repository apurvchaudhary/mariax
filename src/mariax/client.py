import contextlib
from typing import Any, Iterable, Optional, Tuple, List


class DBClient:
    """
    Thin DB-API wrapper. Accepts a DB-API connection (mysqlclient, mariadb, mysql-connector).
    Keeps parameterization and simple helpers for execute/fetch.
    """

    def __init__(self, connection):
        self.conn = connection

    def _safe_commit(self):
        try:
            self.conn.commit()
        except Exception:
            pass  # Some MariaDB drivers auto-commit for DDL

    def execute(self, sql: str, params: Optional[Iterable[Any]] = None) -> int:
        with contextlib.closing(self.conn.cursor()) as cur:
            cur.execute(sql, params or ())
            self._safe_commit()
            return cur.rowcount

    def fetchall(self, sql: str, params: Optional[Iterable[Any]] = None) -> List[Tuple]:
        with contextlib.closing(self.conn.cursor()) as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()

    def fetchone(self, sql: str, params: Optional[Iterable[Any]] = None):
        with contextlib.closing(self.conn.cursor()) as cur:
            cur.execute(sql, params or ())
            return cur.fetchone()
