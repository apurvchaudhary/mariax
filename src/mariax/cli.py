import argparse
from os import getenv

from mariax.client import DBClient
from mariax.ddl import create_vector_index_sql, drop_vector_index_sql


def get_connection(sync_dj_con: bool = True, using: str = "default"):
    """Return a database connection.

    - If sync_dj_con is True, attempts to use a Django-managed connection.
    - Otherwise, falls back to a direct mysql-connector connection using
      environment variables.

    This function lazily imports Django and mysql-connector to keep the CLI
    usable even when these optional dependencies are not installed.
    """
    if sync_dj_con:
        try:
            from django.db import connections  # type: ignore
        except Exception as e:  # ImportError or ImproperlyConfigured
            raise RuntimeError(
                "Django connection requested but Django is not available or not configured"
            ) from e
        return connections[using]

    # Non-Django direct connection path
    try:
        import mysql.connector as _mysql  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "mysql-connector-python is required for direct connections. Install it or enable Django mode."
        ) from e

    host = getenv("MARIADB_HOST", "localhost")
    user = getenv("MARIADB_USER", "maria")
    password = getenv("MARIADB_PASSWORD", "maria")
    db = getenv("MARIADB_DB", "maria")
    return _mysql.connect(host=host, user=user, password=password, database=db)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="mariax")
    sub = parser.add_subparsers(dest="cmd", required=True)

    create = sub.add_parser("create-index")
    create.add_argument("--table", required=True)
    create.add_argument("--name", required=True)
    create.add_argument("--fields", required=True, help="comma-separated field names")
    create.add_argument("--distance", default="cosine")
    create.add_argument("--m", type=int, default=None)

    drop = sub.add_parser("drop-index")
    drop.add_argument("--table", required=True)
    drop.add_argument("--name", required=True)

    args = parser.parse_args(argv)

    # Prefer Django connection if Django is installed/configured; otherwise fallback.
    try:
        conn = get_connection(sync_dj_con=True)
    except Exception:
        conn = get_connection(sync_dj_con=False)

    db = DBClient(conn)
    if args.cmd == "create-index":
        fields = [f.strip() for f in args.fields.split(",") if f.strip()]
        sql = create_vector_index_sql(args.table, args.name, fields, distance=args.distance, m=args.m)
        print("Executing:", sql)
        db.execute(sql)
    elif args.cmd == "drop-index":
        sql = drop_vector_index_sql(args.table, args.name)
        print("Executing:", sql)
        db.execute(sql)
