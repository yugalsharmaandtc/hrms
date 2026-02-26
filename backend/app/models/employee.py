from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id          = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True, nullable=False)
    full_name   = Column(String, nullable=False)
    email       = Column(String, unique=True, index=True, nullable=False)
    department  = Column(String, nullable=False)
    position    = Column(String, nullable=True)
    phone       = Column(String, nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())

    attendance_records = relationship(
        "Attendance",
        back_populates="employee",
        cascade="all, delete-orphan"
    )