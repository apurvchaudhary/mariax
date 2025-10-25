import argparse
from os import getenv

import mysql.connector as _mysql
from django.db import connections
from mariax.client import DBClient
from mariax.ddl import create_vector_index_sql, drop_vector_index_sql


def get_connection(sync_dj_con=True, using="default"):
    """
    Retrieves and returns a database connection. Allows the option to retrieve a direct MySQL
    connection or a Django-managed database connection.
    """
    if not sync_dj_con:
        host = getenv("MARIADB_HOST", "localhost")
        user = getenv("MARIADB_USER", "maria")
        password = getenv("MARIADB_PASSWORD", "maria")
        db = getenv("MARIADB_DB", "maria")
        return _mysql.connect(host=host, user=user, password=password, database=db)
    return connections[using]


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
    conn = get_connection()
    db = DBClient(conn)
    if args.cmd == "create-index":
        fields = [f.strip() for f in args.fields.split(",")]
        sql = create_vector_index_sql(args.table, args.name, fields, distance=args.distance, m=args.m)
        print("Executing:", sql)
        db.execute(sql)
    elif args.cmd == "drop-index":
        sql = drop_vector_index_sql(args.table, args.name)
        print("Executing:", sql)
        db.execute(sql)
