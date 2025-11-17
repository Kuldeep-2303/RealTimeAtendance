from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Ensure your PostgreSQL server is running. On macOS with Homebrew, you can start it with:
# brew services start postgresql

# --- Database Configuration ---
# It's recommended to use environment variables for database credentials for security.
# The DATABASE_URL format is: "postgresql+psycopg2://<user>:<password>@<host>:<port>/<database>"
#
# Example for a user 'myuser' with password 'mypassword' on localhost:
# DATABASE_URL="postgresql+psycopg2://myuser:mypassword@localhost:5432/attendance_db"
#
# The code below will use the DATABASE_URL from your environment variables.
# If it's not set, it will fall back to a default value.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:admin@localhost:5432/attendance_db")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
