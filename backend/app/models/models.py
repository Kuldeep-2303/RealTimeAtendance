from sqlalchemy import Column, Integer, String, Date, DateTime, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    face_embeddings = Column(LargeBinary, nullable=False)

    attendance = relationship("AttendanceLog", back_populates="user")


class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    emotion = Column(String, nullable=False)
    position = Column(String, nullable=False)

    user = relationship("User", back_populates="attendance")
