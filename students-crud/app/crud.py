from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas


class DuplicateEmailError(Exception):
    pass


class ContactRequiredError(Exception):
    pass


def get_student(db: Session, student_id: int) -> Optional[models.Student]:
    return db.get(models.Student, student_id)


def get_students(
    db: Session,
    name: Optional[str] = None,
    course: Optional[str] = None,
    born_after: Optional[date] = None,
    born_before: Optional[date] = None,
    skip: int = 0,
    limit: int = 50,
) -> list[models.Student]:
    stmt = select(models.Student)
    if name:
        stmt = stmt.where(models.Student.name.ilike(f"%{name}%"))
    if course:
        stmt = stmt.where(models.Student.course.ilike(f"%{course}%"))
    if born_after:
        stmt = stmt.where(models.Student.date_of_birth > born_after)
    if born_before:
        stmt = stmt.where(models.Student.date_of_birth < born_before)
    stmt = stmt.order_by(models.Student.id).offset(skip).limit(limit)
    return list(db.scalars(stmt))


def _email_taken(db: Session, email: Optional[str], exclude_id: Optional[int] = None) -> bool:
    if not email:
        return False
    stmt = select(models.Student.id).where(models.Student.email == email)
    if exclude_id is not None:
        stmt = stmt.where(models.Student.id != exclude_id)
    return db.scalar(stmt) is not None


def create_student(db: Session, data: schemas.StudentCreate) -> models.Student:
    if _email_taken(db, data.email):
        raise DuplicateEmailError(data.email)
    student = models.Student(**data.model_dump())
    db.add(student)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateEmailError(data.email)
    db.refresh(student)
    return student


def replace_student(db: Session, student: models.Student, data: schemas.StudentCreate) -> models.Student:
    """PUT: replace every field."""
    if _email_taken(db, data.email, exclude_id=student.id):
        raise DuplicateEmailError(data.email)
    for key, value in data.model_dump().items():
        setattr(student, key, value)
    return _commit(db, student, data.email)


def update_student(db: Session, student: models.Student, data: schemas.StudentUpdate) -> models.Student:
    """PATCH: change only the fields that were sent."""
    changes = data.model_dump(exclude_unset=True)
    new_email = changes.get("email", student.email)
    new_phone = changes.get("phone", student.phone)
    if not new_email and not new_phone:
        raise ContactRequiredError()
    if _email_taken(db, new_email, exclude_id=student.id):
        raise DuplicateEmailError(new_email)
    for key, value in changes.items():
        setattr(student, key, value)
    return _commit(db, student, new_email)


def _commit(db: Session, student: models.Student, email: Optional[str]) -> models.Student:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateEmailError(email)
    db.refresh(student)
    return student


def delete_student(db: Session, student: models.Student) -> None:
    db.delete(student)
    db.commit()
