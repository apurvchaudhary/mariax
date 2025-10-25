import argparse
import os
from .client import DBClient
from .ddl import create_vector_index_sql, drop_vector_index_sql

# CLI using mysql-connector for convenience
import mysql.connector as _mysql


def get_conn_from_env():
    host = os.getenv("MARIADB_HOST", "127.0.0.1")
    user = os.getenv("MARIADB_USER", "test")
    password = os.getenv("MARIADB_PASSWORD", "test")
    db = os.getenv("MARIADB_DB", "test")
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
    conn = get_conn_from_env()
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
