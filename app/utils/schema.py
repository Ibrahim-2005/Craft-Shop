from sqlalchemy import inspect, text

from app import db


ADMIN_COLUMNS = {
    "username": "VARCHAR(80)",
    "reset_token_hash": "VARCHAR(255)",
    "reset_token_expires_at": "TIMESTAMP",
    "is_active_account": "BOOLEAN DEFAULT TRUE",
}

ORDER_COLUMNS = {
    "customer_id": "INTEGER",
}


def ensure_runtime_schema():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    with db.engine.begin() as connection:
        if "admin" in tables:
            existing = {column["name"] for column in inspector.get_columns("admin")}
            for column, column_type in ADMIN_COLUMNS.items():
                if column not in existing:
                    connection.execute(text(f'ALTER TABLE "admin" ADD COLUMN {column} {column_type}'))
        if "order" in tables:
            existing = {column["name"] for column in inspector.get_columns("order")}
            for column, column_type in ORDER_COLUMNS.items():
                if column not in existing:
                    connection.execute(text(f'ALTER TABLE "order" ADD COLUMN {column} {column_type}'))
