from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate

def get_all_employees(db: Session):
    return db.query(Employee).order_by(Employee.created_at.desc()).all()

def get_employee_by_id(db: Session, employee_id: int):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

def create_employee(db: Session, data: EmployeeCreate):
    existing = db.query(Employee).filter(
        (Employee.employee_id == data.employee_id) | (Employee.email == data.email)
    ).first()
    if existing:
        if existing.employee_id == data.employee_id:
            raise HTTPException(status_code=400, detail="Employee ID already exists")
        raise HTTPException(status_code=400, detail="Email address already registered")

    employee = Employee(**data.model_dump())
    db.add(employee)
    try:
        db.commit()
        db.refresh(employee)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Employee with this ID or email already exists")
    return employee

def update_employee(db: Session, employee_id: int, data: EmployeeUpdate):
    employee = get_employee_by_id(db, employee_id)
    update_data = data.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] != employee.email:
        existing = db.query(Employee).filter(Employee.email == update_data["email"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already used by another employee")

    for key, value in update_data.items():
        setattr(employee, key, value)
    db.commit()
    db.refresh(employee)
    return employee

def delete_employee(db: Session, employee_id: int):
    employee = get_employee_by_id(db, employee_id)
    db.delete(employee)
    db.commit()
    return {"message": f"Employee {employee.full_name} deleted successfully"}

def get_employee_stats(db: Session):
    from app.models.attendance import Attendance
    from sqlalchemy import func
    from datetime import date

    total = db.query(Employee).count()
    departments = db.query(Employee.department, func.count(Employee.id)).group_by(Employee.department).all()
    today_present = db.query(Attendance).filter(Attendance.date == date.today(), Attendance.status == "Present").count()
    today_absent  = db.query(Attendance).filter(Attendance.date == date.today(), Attendance.status == "Absent").count()

    return {
        "total_employees": total,
        "today_present": today_present,
        "today_absent": today_absent,
        "departments": [{"name": d[0], "count": d[1]} for d in departments],
    }