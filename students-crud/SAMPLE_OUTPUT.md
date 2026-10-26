# Sample Output

Real output captured from running this project (Python 3.12). Your timestamps and process IDs will differ.

## 1. Seeding dummy data

```
$ python seed.py
Inserted 6 dummy students.
```

## 2. Starting the server

```
$ python -m uvicorn app.main:app --reload
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Open http://127.0.0.1:8000/docs to see the Swagger page with all endpoints.

## 3. API requests and responses

### Create a student

```
POST /students
Body: {"name":"Test Student","date_of_birth":"2004-05-17","email":"test@example.com","phone":"+91 98765 43210","course":"Computer Science"}
```

Response: **201**

```json
{
    "id": 7,
    "name": "Test Student",
    "date_of_birth": "2004-05-17",
    "email": "test@example.com",
    "phone": "+91 98765 43210",
    "course": "Computer Science",
    "address": null,
    "enrollment_date": null
}
```

### Create with a duplicate email (error)

```
POST /students
Body: {"name":"Another","date_of_birth":"2004-01-01","email":"test@example.com"}
```

Response: **409**

```json
{
    "detail": "A student with this email already exists"
}
```

### Create with invalid data (error)

```
POST /students
Body: {"name":"Bad Email","date_of_birth":"2004-01-01","email":"not-an-email"}
```

Response: **422**

```json
{
    "detail": [
        {
            "type": "value_error",
            "loc": [
                "body",
                "email"
            ],
            "msg": "value is not a valid email address: An email address must have an @-sign.",
            "input": "not-an-email",
            "ctx": {
                "reason": "An email address must have an @-sign."
            }
        }
    ]
}
```

### List students filtered by course

```
GET /students?course=computer
```

Response: **200**

```json
[
    {
        "id": 1,
        "name": "Aarav Sharma",
        "date_of_birth": "2004-05-17",
        "email": "aarav@example.com",
        "phone": "+91 90000 00001",
        "course": "Computer Science",
        "address": null,
        "enrollment_date": "2023-07-01"
    },
    {
        "id": 3,
        "name": "Karthik Raman",
        "date_of_birth": "2003-01-25",
        "email": "karthik@example.com",
        "phone": null,
        "course": "Computer Science",
        "address": null,
        "enrollment_date": "2022-07-01"
    },
    {
        "id": 7,
        "name": "Test Student",
        "date_of_birth": "2004-05-17",
        "email": "test@example.com",
        "phone": "+91 98765 43210",
        "course": "Computer Science",
        "address": null,
        "enrollment_date": null
    }
]
```

### View one student

```
GET /students/1
```

Response: **200**

```json
{
    "id": 1,
    "name": "Aarav Sharma",
    "date_of_birth": "2004-05-17",
    "email": "aarav@example.com",
    "phone": "+91 90000 00001",
    "course": "Computer Science",
    "address": null,
    "enrollment_date": "2023-07-01"
}
```

### Filter by date of birth (born after 2005-01-01)

```
GET /students?born_after=2005-01-01
```

Response: **200**

```json
[
    {
        "id": 2,
        "name": "Diya Patel",
        "date_of_birth": "2005-11-02",
        "email": "diya@example.com",
        "phone": "+91 90000 00002",
        "course": "Information Technology",
        "address": null,
        "enrollment_date": "2023-07-01"
    },
    {
        "id": 4,
        "name": "Meera Iyer",
        "date_of_birth": "2006-08-09",
        "email": "meera@example.com",
        "phone": "+91 90000 00004",
        "course": "Electronics",
        "address": null,
        "enrollment_date": "2024-07-01"
    },
    {
        "id": 5,
        "name": "Rohan Das",
        "date_of_birth": "2005-03-30",
        "email": null,
        "phone": "+91 90000 00005",
        "course": "Mechanical",
        "address": null,
        "enrollment_date": "2023-07-01"
    },
    {
        "id": 6,
        "name": "Sneha Nair",
        "date_of_birth": "2007-12-14",
        "email": "sneha@example.com",
        "phone": "+91 90000 00006",
        "course": "Information Technology",
        "address": null,
        "enrollment_date": "2025-07-01"
    }
]
```

### Partial update (PATCH)

```
PATCH /students/7
Body: {"course":"AI and Data Science"}
```

Response: **200**

```json
{
    "id": 7,
    "name": "Test Student",
    "date_of_birth": "2004-05-17",
    "email": "test@example.com",
    "phone": "+91 98765 43210",
    "course": "AI and Data Science",
    "address": null,
    "enrollment_date": null
}
```

### Full replace (PUT)

```
PUT /students/7
Body: {"name":"Updated Student","date_of_birth":"2003-03-03","email":"updated@example.com"}
```

Response: **200**

```json
{
    "id": 7,
    "name": "Updated Student",
    "date_of_birth": "2003-03-03",
    "email": "updated@example.com",
    "phone": null,
    "course": null,
    "address": null,
    "enrollment_date": null
}
```

### Delete a student

```
DELETE /students/7
```

Response: **204**


### View the deleted student (error)

```
GET /students/7
```

Response: **404**

```json
{
    "detail": "Student 7 not found"
}
```

### Optional AI endpoint without Ollama running

```
POST /ask
Body: {"question":"How many students are there?"}
```

Response: **503**

```json
{
    "detail": "Ollama is not reachable. Start it and run: ollama pull llama3.2:1b"
}
```

## 4. Automated tests

```
$ python -m pytest -v
tests/test_students.py::test_homepage_serves_student_dashboard PASSED
tests/test_students.py::test_create_and_get PASSED
tests/test_students.py::test_list_and_filter PASSED
tests/test_students.py::test_put_replaces PASSED
tests/test_students.py::test_patch_partial PASSED
tests/test_students.py::test_patch_cannot_remove_all_contacts PASSED
tests/test_students.py::test_delete PASSED
tests/test_students.py::test_missing_record_404 PASSED
tests/test_students.py::test_duplicate_email_409 PASSED
tests/test_students.py::test_validation_422[bad0] PASSED
tests/test_students.py::test_validation_422[bad1] PASSED
tests/test_students.py::test_validation_422[bad2] PASSED
tests/test_students.py::test_validation_422[bad3] PASSED
tests/test_students.py::test_validation_422[bad4] PASSED
tests/test_students.py::test_ai_context_is_grounded PASSED
tests/test_students.py::test_ask_returns_503_when_ollama_down PASSED
======================== 16 passed, 1 warning in 2.50s =========================
```
