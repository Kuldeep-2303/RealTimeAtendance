from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import sys
import numpy as np
from sqlalchemy.exc import OperationalError

from app.routes import user, face_cache
from app.models.database import Base, engine, SessionLocal
from app.utils.database import get_all_users
from app.models import models

logging.basicConfig(level=logging.INFO)

# Initialize FastAPI app
app = FastAPI(title="Smart Attendance API")

# On startup: load known faces into cache
@app.on_event("startup")
def on_startup():
    """
    On application startup, load all user face embeddings from the database
    into an in-memory cache for faster recognition.
    """
    logging.info("Connecting to the database and setting up tables...")
    try:
        # This will try to connect to the DB and raise an error if it fails
        # WARNING: The following lines will drop and recreate tables.
        # This is for development only and will delete all existing data.
        with engine.connect() as connection:
            # Create all database tables if they don't exist
            # models.Base.metadata.drop_all(bind=engine) # Uncomment to drop all tables
            models.Base.metadata.create_all(bind=engine)
    except OperationalError as e:
        logging.error(f"Could not connect to the database: {e}")
        logging.error("Please ensure the database server is running and the DATABASE_URL is correct.")
        sys.exit(1)

    logging.info("Loading known faces into memory cache...")
    db = SessionLocal()
    try:
        users = get_all_users(db)
        for u in users:
            face_cache.known_face_encodings.append(
                np.frombuffer(u.face_embeddings, dtype=np.float64)
            )
            face_cache.known_face_users.append(u)
        logging.info(f"Loaded {len(face_cache.known_face_users)} faces into cache.")
    finally:
        db.close()


# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Smart Attendance System API"}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],   # Allows all methods
    allow_headers=["*"],   # Allows all headers
)

# Mount the directory for serving uploaded images
app.mount("/uploaded_images", StaticFiles(directory="uploaded_images"), name="uploaded_images")

# Include user-related routes
app.include_router(user.router, prefix="/api", tags=["users"])
