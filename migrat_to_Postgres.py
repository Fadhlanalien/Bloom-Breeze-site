#!/usr/bin/env python3
"""
Migrate database.db (SQLite) into PostgreSQL.

Schema: users, products, variants, shipping, orders, order_status_history,
admins, product_images, product_videos.

Requirements:
    pip install "psycopg[binary]"

Usage (recommended, e.g. for Neon — paste your connection string):
    python migrate_to_postgres.py \
        --sqlite-file database.db \
        --pg-conn-string "postgresql://user:password@host/dbname?sslmode=require"

Usage (alternative, individual flags):
    python migrate_to_postgres.py \
        --sqlite-file database.db \
        --pg-host localhost \
        --pg-port 5432 \
        --pg-db mydb \
        --pg-user myuser \
        --pg-password mypassword

You can also set DATABASE_URL, or PGHOST / PGPORT / PGDATABASE / PGUSER /
PGPASSWORD, as environment variables instead of passing them on the command line.

By default this will CREATE the tables if they don't exist yet. Pass
--drop-existing if you want it to drop and recreate them (careful:
this deletes any existing data in those tables on the Postgres side).
"""

import argparse
import os
import sqlite3
import sys

try:
    import psycopg
except ImportError:
    sys.exit("Missing dependency. Install it with: pip install \"psycopg[binary]\"")


# Tables in dependency order: parents before children, so foreign keys
# don't fail when we insert data (and so DROP CASCADE tears down cleanly
# in reverse order).
TABLE_ORDER = [
    "users",
    "admins",
    "products",
    "variants",
    "shipping",
    "orders",
    "order_status_history",
    "product_images",
    "product_videos",
]

CREATE_STATEMENTS = {
    "users": """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            full_name TEXT NOT NULL,
            mobile_number TEXT NOT NULL,
            address_line01 TEXT NOT NULL,
            address_line02 TEXT,
            city TEXT NOT NULL,
            country TEXT NOT NULL,
            email TEXT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
    """,
    "admins": """
        CREATE TABLE IF NOT EXISTS admins (
            id SERIAL PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            mobile_number TEXT NOT NULL,
            address_line01 TEXT NOT NULL,
            address_line02 TEXT,
            city TEXT NOT NULL,
            country TEXT NOT NULL,
            admin_name TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            admin_code TEXT NOT NULL
        );
    """,
    "products": """
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            brand TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            file_path TEXT NOT NULL
        );
    """,
    "variants": """
        CREATE TABLE IF NOT EXISTS variants (
            id SERIAL PRIMARY KEY,
            product_id INTEGER NOT NULL REFERENCES products(id),
            size TEXT NOT NULL,
            colour TEXT,
            price INTEGER NOT NULL,
            stock TEXT NOT NULL,
            "SKU" TEXT NOT NULL
        );
    """,
    "shipping": """
        CREATE TABLE IF NOT EXISTS shipping (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            address_line01 TEXT NOT NULL,
            address_line02 TEXT,
            city TEXT NOT NULL,
            country TEXT NOT NULL
        );
    """,
    "orders": """
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            product_id INTEGER NOT NULL REFERENCES products(id),
            shipping_id INTEGER NOT NULL REFERENCES shipping(id),
            quantity INTEGER NOT NULL,
            total_price INTEGER NOT NULL,
            status TEXT NOT NULL,
            order_date TEXT
        );
    """,
    "order_status_history": """
        CREATE TABLE IF NOT EXISTS order_status_history (
            id SERIAL PRIMARY KEY,
            order_id INTEGER NOT NULL REFERENCES orders(id),
            status TEXT NOT NULL,
            updated_date TEXT NOT NULL
        );
    """,
    "product_images": """
        CREATE TABLE IF NOT EXISTS product_images (
            id SERIAL PRIMARY KEY,
            product_id INTEGER NOT NULL REFERENCES products(id),
            file_path TEXT NOT NULL
        );
    """,
    "product_videos": """
        CREATE TABLE IF NOT EXISTS product_videos (
            id SERIAL PRIMARY KEY,
            product_id INTEGER NOT NULL REFERENCES products(id),
            file_path_video TEXT NOT NULL
        );
    """,
}

# Column order per table (must match SELECT order from SQLite and INSERT
# order into Postgres).
TABLE_COLUMNS = {
    "users": ["id", "full_name", "mobile_number", "address_line01", "address_line02",
              "city", "country", "email", "username", "password"],
    "admins": ["id", "full_name", "email", "mobile_number", "address_line01",
               "address_line02", "city", "country", "admin_name", "password", "admin_code"],
    "products": ["id", "brand", "name", "description", "file_path"],
    "variants": ["id", "product_id", "size", "colour", "price", "stock", "SKU"],
    "shipping": ["id", "user_id", "address_line01", "address_line02", "city", "country"],
    "orders": ["id", "user_id", "product_id", "shipping_id", "quantity",
               "total_price", "status", "order_date"],
    "order_status_history": ["id", "order_id", "status", "updated_date"],
    "product_images": ["id", "product_id", "file_path"],
    "product_videos": ["id", "product_id", "file_path_video"],
}


def quote_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def migrate_table(sconn, pconn, table, batch_size):
    columns = TABLE_COLUMNS[table]
    quoted_cols = [quote_ident(c) for c in columns]

    scur = sconn.cursor()
    scur.execute(f'SELECT {", ".join(quoted_cols)} FROM "{table}"')

    pcur = pconn.cursor()
    placeholders = ", ".join(["%s"] * len(columns))
    insert_sql = f"INSERT INTO {quote_ident(table)} ({', '.join(quoted_cols)}) VALUES ({placeholders})"

    total = 0
    while True:
        rows = scur.fetchmany(batch_size)
        if not rows:
            break
        pcur.executemany(insert_sql, rows)
        pconn.commit()
        total += len(rows)

    print(f"  -> {table}: {total} row(s) migrated")
    return total


def reset_sequence(pconn, table):
    """After inserting explicit IDs, bump the SERIAL sequence so future
    auto-inserts don't collide with migrated rows."""
    pcur = pconn.cursor()
    pcur.execute(f"""
        SELECT setval(
            pg_get_serial_sequence('{table}', 'id'),
            COALESCE((SELECT MAX(id) FROM {quote_ident(table)}), 1),
            (SELECT MAX(id) IS NOT NULL FROM {quote_ident(table)})
        );
    """)
    pconn.commit()


def main():
    parser = argparse.ArgumentParser(description="Migrate SQLite e-commerce DB to PostgreSQL")
    parser.add_argument("--sqlite-file", required=True, help="Path to database.db")
    parser.add_argument(
        "--pg-conn-string",
        default=os.environ.get("DATABASE_URL"),
        help="Full PostgreSQL connection string, e.g. Neon's "
             "'postgresql://user:password@host/dbname?sslmode=require'. "
             "If provided, --pg-host/--pg-db/--pg-user/--pg-password are ignored.",
    )
    parser.add_argument("--pg-host", default=os.environ.get("PGHOST", "localhost"))
    parser.add_argument("--pg-port", default=os.environ.get("PGPORT", "5432"))
    parser.add_argument("--pg-db", default=os.environ.get("PGDATABASE"))
    parser.add_argument("--pg-user", default=os.environ.get("PGUSER"))
    parser.add_argument("--pg-password", default=os.environ.get("PGPASSWORD"))
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument(
        "--drop-existing",
        action="store_true",
        help="Drop and recreate all tables in PostgreSQL before migrating (deletes existing data there)",
    )
    args = parser.parse_args()

    if not args.pg_conn_string and (not args.pg_db or not args.pg_user):
        sys.exit(
            "You must provide either --pg-conn-string (recommended for Neon), "
            "or --pg-db and --pg-user (or set PGDATABASE / PGUSER)."
        )

    if not os.path.exists(args.sqlite_file):
        sys.exit(f"SQLite file not found: {args.sqlite_file}")

    print(f"Connecting to SQLite file: {args.sqlite_file}")
    sconn = sqlite3.connect(args.sqlite_file)

    if args.pg_conn_string:
        print("Connecting to PostgreSQL using connection string...")
        pconn = psycopg.connect(args.pg_conn_string)
    else:
        print(f"Connecting to PostgreSQL at {args.pg_host}:{args.pg_port}/{args.pg_db}")
        pconn = psycopg.connect(
            host=args.pg_host,
            port=args.pg_port,
            dbname=args.pg_db,
            user=args.pg_user,
            password=args.pg_password,
            sslmode="require",
        )
    pcur = pconn.cursor()

    if args.drop_existing:
        print("Dropping existing tables (if any)...")
        for table in reversed(TABLE_ORDER):
            pcur.execute(f"DROP TABLE IF EXISTS {quote_ident(table)} CASCADE;")
        pconn.commit()

    print("Creating tables...")
    for table in TABLE_ORDER:
        pcur.execute(CREATE_STATEMENTS[table])
    pconn.commit()

    print("\nMigrating data...")
    total_rows = 0
    for table in TABLE_ORDER:
        total_rows += migrate_table(sconn, pconn, table, args.batch_size)

    print("\nResetting auto-increment sequences...")
    for table in TABLE_ORDER:
        reset_sequence(pconn, table)

    print(f"\nMigration complete. Total rows migrated: {total_rows}")

    sconn.close()
    pconn.close()


if __name__ == "__main__":
    main()
