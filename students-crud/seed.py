"""Fill the database with DUMMY students (all fake data) for testing."""
from datetime import date

from app.database import Base, SessionLocal, engine
from app.models import Student

SAMPLE = [
    ("Aarav Sharma", date(2004, 5, 17), "aarav@example.com", "+91 90000 00001", "Computer Science", date(2023, 7, 1)),
    ("Diya Patel", date(2005, 11, 2), "diya@example.com", "+91 90000 00002", "Information Technology", date(2023, 7, 1)),
    ("Karthik Raman", date(2003, 1, 25), "karthik@example.com", None, "Computer Science", date(2022, 7, 1)),
    ("Meera Iyer", date(2006, 8, 9), "meera@example.com", "+91 90000 00004", "Electronics", date(2024, 7, 1)),
    ("Rohan Das", date(2005, 3, 30), None, "+91 90000 00005", "Mechanical", date(2023, 7, 1)),
    ("Sneha Nair", date(2007, 12, 14), "sneha@example.com", "+91 90000 00006", "Information Technology", date(2025, 7, 1)),
]


def main():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.query(Student).count():
            print("Database already has data - skipping seed.")
            return
        for name, dob, email, phone, course, enrolled in SAMPLE:
            db.add(Student(name=name, date_of_birth=dob, email=email, phone=phone,
                           course=course, enrollment_date=enrolled))
        db.commit()
        print(f"Inserted {len(SAMPLE)} dummy students.")


if __name__ == "__main__":
    main()
