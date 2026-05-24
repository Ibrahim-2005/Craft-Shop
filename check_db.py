from sqlalchemy import text

from app import create_app, db


app = create_app()

with app.app_context():
    with db.engine.connect() as connection:
        if db.engine.dialect.name == "postgresql":
            current_database = connection.execute(text("select current_database()")).scalar()
            print(f"Connected to PostgreSQL database: {current_database}")
        else:
            print(f"Connected to {db.engine.dialect.name}: {db.engine.url.database}")
