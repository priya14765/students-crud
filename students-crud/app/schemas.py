from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

PHONE_PATTERN = r"^\+?[0-9][0-9\s\-]{6,18}$"


def _check_dob(value: Optional[date]) -> Optional[date]:
    if value is not None and value >= date.today():
        raise ValueError("date_of_birth must be in the past")
    return value


def _clean_name(value: Optional[str]) -> Optional[str]:
    if value is None:
        return value
    value = value.strip()
    if not value:
        raise ValueError("name must not be blank")
    return value


class StudentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100, examples=["Aarav Sharma"])
    date_of_birth: date = Field(examples=["2004-05-17"])
    email: Optional[EmailStr] = Field(default=None, examples=["aarav@example.com"])
    phone: Optional[str] = Field(default=None, pattern=PHONE_PATTERN, examples=["+91 98765 43210"])
    course: Optional[str] = Field(default=None, max_length=100, examples=["Computer Science"])
    address: Optional[str] = Field(default=None, max_length=255)
    enrollment_date: Optional[date] = None

    _v_name = field_validator("name")(_clean_name)
    _v_dob = field_validator("date_of_birth")(_check_dob)

    @field_validator("email")
    @classmethod
    def _lower_email(cls, v):
        return v.lower() if v else v

    @model_validator(mode="after")
    def _need_contact(self):
        if not self.email and not self.phone:
            raise ValueError("provide at least one contact: email or phone")
        return self


class StudentUpdate(BaseModel):
    """All fields optional - used for PATCH (partial update)."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, pattern=PHONE_PATTERN)
    course: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=255)
    enrollment_date: Optional[date] = None

    _v_name = field_validator("name")(_clean_name)
    _v_dob = field_validator("date_of_birth")(_check_dob)

    @field_validator("email")
    @classmethod
    def _lower_email(cls, v):
        return v.lower() if v else v

    @model_validator(mode="after")
    def _required_not_null(self):
        for field in ("name", "date_of_birth"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class StudentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    date_of_birth: date
    email: Optional[str] = None
    phone: Optional[str] = None
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: Optional[date] = None


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500, examples=["How many students are there?"])


class AskResponse(BaseModel):
    question: str
    answer: str
    model: str
    records_used: list[int]

