from datetime import date
from typing import Optional

from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    course: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    enrollment_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
