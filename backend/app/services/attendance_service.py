from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate
from datetime import date

def get_all_attendance(db: Session, employee_id: int = None, filter_date: date = None):
    query = db.query(Attendance)
    if employee_id:
        query = query.filter(Attendance.employee_id == employee_id)
    if filter_date:
        query = query.filter(Attendance.date == filter_date)

    records = query.order_by(Attendance.date.desc()).all()
    result = []
    for record in records:
        emp = db.query(Employee).filter(Employee.id == record.employee_id).first()
        result.append({
            "id": record.id,
            "employee_id": record.employee_id,
            "date": record.date,
            "status": record.status,
            "notes": record.notes,
            "created_at": record.created_at,
            "employee_name": emp.full_name if emp else None,
            "employee_emp_id": emp.employee_id if emp else None,
        })
    return result

def mark_attendance(db: Session, data: AttendanceCreate):
    employee = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    existing = db.query(Attendance).filter(
        Attendance.employee_id == data.employee_id,
        Attendance.date == data.date
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Attendance already marked for {employee.full_name} on {data.date}. Use edit to update."
        )

    record = Attendance(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "employee_id": record.employee_id,
        "date": record.date,
        "status": record.status,
        "notes": record.notes,
        "created_at": record.created_at,
        "employee_name": employee.full_name,
        "employee_emp_id": employee.employee_id,
    }

def update_attendance(db: Session, attendance_id: int, data: AttendanceUpdate):
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance record not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)

    emp = db.query(Employee).filter(Employee.id == record.employee_id).first()
    return {
        "id": record.id,
        "employee_id": record.employee_id,
        "date": record.date,
        "status": record.status,
        "notes": record.notes,
        "created_at": record.created_at,
        "employee_name": emp.full_name if emp else None,
        "employee_emp_id": emp.employee_id if emp else None,
    }

def delete_attendance(db: Session, attendance_id: int):
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    db.delete(record)
    db.commit()
    return {"message": "Attendance record deleted"}

def get_employee_attendance_summary(db: Session, employee_id: int):
    from sqlalchemy import func
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    records = db.query(Attendance.status, func.count(Attendance.id)).filter(
        Attendance.employee_id == employee_id
    ).group_by(Attendance.status).all()

    summary = {"Present": 0, "Absent": 0, "Half Day": 0, "Late": 0}
    for status, count in records:
        summary[status] = count

    return {
        "employee_id": employee_id,
        "employee_name": employee.full_name,
        "summary": summary,
        "total_days": sum(summary.values())
    }