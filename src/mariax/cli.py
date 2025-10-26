import argparse
from os import getenv

from django.core.exceptions import ImproperlyConfigured
from django.db.utils import OperationalError, ProgrammingError

from mariax.client import DBClient
from mariax.ddl import create_vector_index_sql, drop_vector_index_sql


def get_connection(sync_dj_con: bool = True, using: str = "default"):
    """
    Gets a database connection, either using Django's ORM or a direct connection
    to a MariaDB database. This function dynamically determines the connection
    method depending on the `sync_dj_con` parameter.

    - If `sync_dj_con` is enabled, it attempts to fetch the database connection
      from Django using the given alias defined in the `using` parameter.
    - Otherwise, it establishes a direct connection to a MariaDB instance using
      environment variables for the connection configuration.

    :param sync_dj_con: Determines whether to synchronize the connection using
        Django's ORM (True) or establish a direct database connection (False).
    :param using: The alias of the database connection in Django's configuration
        when `sync_dj_con` is True. Defaults to "default".
    :return: A database connection object obtained either from Django's ORM
        or a direct connection to MariaDB.
    :raises RuntimeError: If Django is requested but not available or improperly
        configured, or if `mysql-connector-python` is not installed for a direct
        connection.
    """
    if sync_dj_con:
        try:
            from django.db import connections  # type: ignore
        except Exception as e:  # ImportError or ImproperlyConfigured
            raise RuntimeError("Django connection requested but Django is not available or not configured") from e
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
    """
    The main entry point for the script that offers two subcommands: `create-index` and
    `drop-index` for managing vector-based indices in a database table. This function
    handles command-line arguments, establishes a database connection, and executes
    the respective SQL operations based on the provided command.

    :param argv: List of command-line arguments passed to the script. If None, it defaults
        to the system arguments. Should include the commands (`create-index` or
        `drop-index`) with their respective options.
    :type argv: List[str] or None

    :return: None/raise
    """
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
    except (ModuleNotFoundError, ImproperlyConfigured, OperationalError, ProgrammingError):
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
    else:
        raise ValueError(f"Unknown command: {args.cmd}")
