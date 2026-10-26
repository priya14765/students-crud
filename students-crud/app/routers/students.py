from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/students", tags=["Students"])


def _get_or_404(db: Session, student_id: int):
    student = crud.get_student(db, student_id)
    if student is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Student {student_id} not found")
    return student


def _handle(exc: Exception):
    if isinstance(exc, crud.DuplicateEmailError):
        raise HTTPException(status.HTTP_409_CONFLICT, "A student with this email already exists")
    if isinstance(exc, crud.ContactRequiredError):
        raise HTTPException(422, "Student must keep at least one contact (email or phone)")
    raise exc


@router.post("", response_model=schemas.StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(payload: schemas.StudentCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_student(db, payload)
    except Exception as exc:
        _handle(exc)


@router.get("", response_model=list[schemas.StudentRead])
def list_students(
    name: Optional[str] = Query(None, description="Partial, case-insensitive name match"),
    course: Optional[str] = Query(None, description="Partial, case-insensitive course match"),
    born_after: Optional[date] = Query(None, description="Date of birth strictly after (YYYY-MM-DD)"),
    born_before: Optional[date] = Query(None, description="Date of birth strictly before (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return crud.get_students(db, name, course, born_after, born_before, skip, limit)


@router.get("/{student_id}", response_model=schemas.StudentRead)
def get_student(student_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, student_id)


@router.put("/{student_id}", response_model=schemas.StudentRead)
def replace_student(student_id: int, payload: schemas.StudentCreate, db: Session = Depends(get_db)):
    student = _get_or_404(db, student_id)
    try:
        return crud.replace_student(db, student, payload)
    except Exception as exc:
        _handle(exc)


@router.patch("/{student_id}", response_model=schemas.StudentRead)
def update_student(student_id: int, payload: schemas.StudentUpdate, db: Session = Depends(get_db)):
    student = _get_or_404(db, student_id)
    try:
        return crud.update_student(db, student, payload)
    except Exception as exc:
        _handle(exc)


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = _get_or_404(db, student_id)
    crud.delete_student(db, student)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
