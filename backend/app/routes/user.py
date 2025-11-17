from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form
from sqlalchemy.orm import Session
import numpy as np
from pydantic import BaseModel, ConfigDict
from app.models.database import get_db
from app.models.models import User
from app.services.face_recognition import extract_face_embeddings, find_best_match
from app.services.emotion_detection import detect_emotion
from app.utils.database import create_user, get_all_users, mark_attendance, get_attendance_records
from fastapi.security import OAuth2PasswordRequestForm
from app.utils.auth import authenticate_admin, create_access_token, get_current_admin
from app.services.liveness_detection import is_live_person
from app.routes import face_cache
from app.services.notifications import send_notification
from typing import List, Optional, Tuple
import logging
import pytz # Import pytz for timezone conversion
import io
import os
import shutil
from datetime import datetime, date


router = APIRouter()
ATTENDANCE_IMAGES_DIR = "attendance_images"
UPLOADED_IMAGES_DIR = "uploaded_images"

# Setup logging
logging.basicConfig(level=logging.INFO)

# Define Indian Standard Time (IST) timezone
IST_TIMEZONE = pytz.timezone('Asia/Kolkata')

# ------------------ Pydantic models ------------------
class UserResponse(BaseModel):
    id: int
    name: str
    employee_id: str
    department: str
    date_of_birth: date

    model_config = ConfigDict(arbitrary_types_allowed=True)

class RecognitionResponse(BaseModel):
    message: str
    user: Optional[UserResponse] = None
    position: str

class AttendanceRecord(BaseModel):
    user_id: int
    timestamp: datetime
    emotion: str
    position: str

class MarkAttendanceResponse(BaseModel):
    message: str
    name: Optional[str] = None
    timestamp: Optional[str] = None # Change type to str for formatted timestamp
    emotion: Optional[str] = None

class RegisterResponse(BaseModel):
    message: str
    user_id: int


# ------------------ Helper function ------------------
def _recognize_face_from_file(file: UploadFile, tolerance: float = 0.58) -> Tuple[Optional[User], str]:
    """Helper function to recognize a face from an uploaded file."""
    embeddings, face_position = extract_face_embeddings(file.file, return_position=True)
    if embeddings is None:
        raise HTTPException(status_code=400, detail="No face detected in the image")

    # Match against the in-memory cache
    if not face_cache.known_face_encodings:
        return None, "center"  # No users in DB to match against

    matched_user = find_best_match(embeddings, face_cache.known_face_encodings, face_cache.known_face_users, tolerance)

    # Determine face position
    position = "center"
    if face_position < 0.33:
        position = "left"
    elif face_position > 0.66:
        position = "right"

    return matched_user, position


# ------------------ API Endpoints ------------------
@router.post("/register", response_model=RegisterResponse)
async def register_user(
    name: str = Form(...),
    employee_id: str = Form(...),
    department: str = Form(...),
    date_of_birth: date = Form(...),
    file: UploadFile = None,
    db: Session = Depends(get_db),
):
    if not file:
        raise HTTPException(status_code=400, detail="Face image is required")

    embeddings = extract_face_embeddings(file.file)
    if embeddings is None:
        raise HTTPException(status_code=400, detail="No face detected in the image")

    user = create_user(db, name=name, employee_id=employee_id, department=department, date_of_birth=date_of_birth, face_embeddings=embeddings)

    # Update the in-memory cache with the new user's data
    face_cache.known_face_encodings.append(np.frombuffer(user.face_embeddings, dtype=np.float64))
    face_cache.known_face_users.append(user)
    logging.info(f"User {user.name} added to face cache.")
    return RegisterResponse(message="User registered successfully", user_id=user.id)


@router.post("/recognize", response_model=RecognitionResponse)
async def recognize_user(file: UploadFile, db: Session = Depends(get_db)):
    if not file:
        raise HTTPException(status_code=400, detail="No image file provided.")
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image.")

    try:
        user, position = _recognize_face_from_file(file)

        if user:
            return RecognitionResponse(
                message="User recognized",
                user=UserResponse(id=user.id, name=user.name, employee_id=user.employee_id, department=user.department, date_of_birth=user.date_of_birth),
                position=position
            )
        return RecognitionResponse(message="Unknown", position=position)
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Unexpected error in /recognize: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred during face recognition.")


@router.post("/detect-emotion")
async def detect_emotion_endpoint(file: UploadFile):
    if not file:
        raise HTTPException(status_code=400, detail="Image file is required")
    
    emotion = detect_emotion(file.file)
    if emotion is None:
        raise HTTPException(status_code=400, detail="No face detected in the image")
    
    return {"message": "Emotion detected", "emotion": emotion}


@router.post("/mark-attendance", response_model=MarkAttendanceResponse)
async def mark_attendance_endpoint(
    file: UploadFile,
    db: Session = Depends(get_db)
):
    if not file:
        raise HTTPException(status_code=400, detail="Image file is required")

    file_content = await file.read()

    try:
        liveness_file = io.BytesIO(file_content)
        if not is_live_person(liveness_file):
            raise HTTPException(status_code=400, detail="Liveness detection failed. Please ensure you are a real person.")
        
        recognition_file = io.BytesIO(file_content)
        temp_upload_file = UploadFile(filename=file.filename, file=recognition_file)

        user, position = _recognize_face_from_file(temp_upload_file, tolerance=0.58)
        
        if not user:
            return MarkAttendanceResponse(message="Unknown user, attendance not marked")

        emotion_file = io.BytesIO(file_content)
        emotion = detect_emotion(emotion_file) # This will now return a simple string
        
        attendance = mark_attendance(db, user_id=user.id, emotion=emotion, position=position)
        
        # Convert UTC timestamp to IST and format it for display
        utc_timestamp = attendance.timestamp.replace(tzinfo=pytz.utc) # Ensure it's timezone-aware UTC
        ist_timestamp = utc_timestamp.astimezone(IST_TIMEZONE)
        # Format to a standard ISO 8601 string. This is robust and easily parsed by JavaScript.
        formatted_timestamp = ist_timestamp.isoformat()

        return MarkAttendanceResponse(
            message="Attendance marked successfully",
            name=user.name,
            timestamp=formatted_timestamp,
            emotion=attendance.emotion # Use the emotion stored in the attendance record
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Unexpected error in /mark-attendance: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred while marking attendance.")


@router.post("/mark-attendance-with-id")
async def mark_attendance_with_id(
    user_id: int = Form(...),
    file: UploadFile = Form(...)
):
    os.makedirs(ATTENDANCE_IMAGES_DIR, exist_ok=True)

    timestamp = datetime.now()
    filename = f"user_{user_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
    image_path = os.path.join(ATTENDANCE_IMAGES_DIR, filename)

    try:
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    print(f"Attendance recorded for user_id: {user_id} at {timestamp} with image: {image_path}")

    return {"message": f"Attendance marked for user_id {user_id}", "saved_image_path": image_path}


@router.post("/admin/login")
async def admin_login(form_data: OAuth2PasswordRequestForm = Depends()):
    admin = authenticate_admin(form_data.username, form_data.password)
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": admin["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/admin/dashboard")
async def admin_dashboard(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    attendance_records = get_attendance_records(db)
    return {"attendance_records": attendance_records}


@router.get("/attendance")
async def get_attendance(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    employee_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    attendance_records = get_attendance_records(db)
    return attendance_records


@router.post("/sync-attendance")
async def sync_attendance(attendance_records: List[dict], db: Session = Depends(get_db)):
    return {"message": f"Successfully synced {len(attendance_records)} attendance records."}


@router.post("/upload-image")
async def upload_image(file: UploadFile):
    if not file:
        raise HTTPException(status_code=400, detail="No file was uploaded.")
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Please upload an image."
        )

    try:
        os.makedirs(UPLOADED_IMAGES_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        safe_filename = f"{timestamp}_{os.path.basename(file.filename)}"
        file_path = os.path.join(UPLOADED_IMAGES_DIR, safe_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"message": "Image uploaded successfully", "filename": safe_filename, "path": file_path}

    except Exception as e:
        logging.error(f"Could not save file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")
