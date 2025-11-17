from sqlalchemy.orm import Session
from datetime import datetime
import os
import logging

from app.models.models import User, AttendanceLog
from app.services.face_recognition import extract_face_embeddings


# ------------------ USER FUNCTIONS ------------------ #
def create_user(db: Session, name: str, employee_id: str, department: str, date_of_birth: datetime.date, face_embeddings: bytes) -> User:
    """
    Create a new user with face embeddings.
    """
    # Generate a placeholder email from the employee_id
    email = f"{employee_id}@example.com"
    user = User(
        name=name,
        employee_id=employee_id,
        email=email,
        department=department,
        date_of_birth=date_of_birth,
        face_embeddings=face_embeddings
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_name(db: Session, name: str) -> User:
    """
    Retrieve a single user by their name.
    """
    return db.query(User).filter(User.name == name).first()


def get_user_by_id(db: Session, user_id: int) -> User:
    """
    Retrieve a single user by ID.
    """
    return db.query(User).filter(User.id == user_id).first()


def get_all_users(db: Session):
    """
    Retrieve all users from the database.
    """
    return db.query(User).all()


# ------------------ ATTENDANCE FUNCTIONS ------------------ #
def mark_attendance(db: Session, user_id: int, emotion: str, position: str) -> AttendanceLog:
    """
    Mark attendance for a user in the database.
    """
    attendance = AttendanceLog(
        user_id=user_id,
        emotion=emotion,
        position=position,
        timestamp=datetime.utcnow()  # ensure UTC
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


def get_attendance_records(db: Session):
    """
    Retrieve all attendance records from the database.
    """
    return db.query(AttendanceLog).all()


# ------------------ SEEDING FUNCTIONS ------------------ #
def seed_database_with_known_faces(db: Session, known_faces_dir: str = "known_faces"):
    """
    Loads face images from a directory, computes embeddings, and saves them to the DB.
    The filename (without extension) is used as the user's name.
    """
    if not os.path.isdir(known_faces_dir):
        logging.warning(f"Known faces directory '{known_faces_dir}' not found. Skipping seeding.")
        return

    for filename in os.listdir(known_faces_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            user_name = os.path.splitext(filename)[0].replace("_", " ").title()

            # Check if user already exists
            if get_user_by_name(db, name=user_name):
                logging.info(f"User '{user_name}' already exists in the database. Skipping.")
                continue

            image_path = os.path.join(known_faces_dir, filename)
            try:
                with open(image_path, "rb") as f:
                    embeddings = extract_face_embeddings(f)

                if embeddings:
                    # Generate placeholder email
                    email = f"{user_name.replace(' ', '.').lower()}@example.com"
                    create_user(db, name=user_name, email=email, face_embeddings=embeddings)
                    logging.info(f"Successfully registered user '{user_name}' from {filename}.")
            except Exception as e:
                logging.error(f"Failed to process or register user from {filename}. Error: {e}")
