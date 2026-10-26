# Students Directory — FastAPI + SQLite

A student records management project with a responsive web dashboard and a REST API, built with **FastAPI**, **SQLite**, and **SQLAlchemy**. The optional AI question-answering endpoint uses a local **Ollama** model.

> All sample data is dummy data. Never store real students' personal information.

## Features
- Responsive dashboard at `/` with light/dark themes (saved in the browser)
- Direct access to the student dashboard and API without login or registration
- Create, view, edit, and delete student records from the dashboard
- Student profile quick-view with age, enrollment, address, and one-click email/phone contact
- Upcoming birthday reminders for the next 30 days, linked to each student profile
- Search by name, email, phone, or course; filter by course; sort by name, age, or recently added
- Paginated student list with selectable page size, summary statistics, and CSV export
- Guided CSV import with a downloadable template, preview, row-level validation, and partial-success reporting
- Mobile-friendly student cards, accessible controls, validation feedback, and refresh
- Full CRUD API with persistent SQLite storage (SQLAlchemy ORM)
- Validation: email and phone format, date of birth in the past, at least one contact (email or phone), unique email
- Clear errors: `404` record not found, `409` duplicate email, `422` invalid input
- Filtering (`name`, `course`, `born_after`, `born_before`) and pagination (`skip`, `limit`)
- `PUT` (replace everything) and `PATCH` (update some fields)
- 21 automated tests (pytest)
- Optional `/ask` endpoint: the backend fetches matching records and gives them to a local Ollama model. The model never runs SQL.

---

## 1. Requirements
- **Python 3.10 or newer** (check with `python --version`; on Mac/Linux you may need `python3 --version`)
- **pip** (comes with Python)
- A terminal: Command Prompt / PowerShell (Windows) or Terminal (Mac/Linux)
- Optional: [Ollama](https://ollama.com) for the AI bonus

## 2. Installation (step by step)

### Step 1: Get the project
Unzip `students-crud.zip`, or clone your GitHub repo. Then open a terminal **inside the project folder** (the folder that contains `app/`, `requirements.txt` and `seed.py`).

```bash
cd students-crud
```

### Step 2: Create a virtual environment
**Windows (PowerShell or Command Prompt):**
```bash
python -m venv .venv
.venv\Scripts\activate
```
If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` once, then activate again.

**Mac / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```
You should now see `(.venv)` at the start of your prompt.

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 (optional): Load dummy data
```bash
python seed.py
```
This inserts 6 fake students. The file `students.db` is created automatically.

### Step 5: Start the server
```bash
python -m uvicorn app.main:app --reload
```
Leave this terminal open. You should see `Uvicorn running on http://127.0.0.1:8001`.

### Step 6: Open the app
- Open **http://127.0.0.1:8001** for the student dashboard.
- Open **http://127.0.0.1:8001/docs** for interactive API documentation (Swagger UI).

### Step 7: Run the tests (optional)
Open a second terminal in the same folder, activate the virtual environment, then run:
```bash
python -m pytest -q
```
Expected result: all tests pass.

### Expected output (how to know it worked)
| Step | You should see |
|---|---|
| `python seed.py` | `Inserted 6 dummy students.` |
| Start the server | `Uvicorn running on http://127.0.0.1:8000` and `Application startup complete.` |
| Open `http://127.0.0.1:8000` | Student directory dashboard with search, filters, and records |
| Open `http://127.0.0.1:8000/docs` | Swagger page listing POST/GET/PUT/PATCH/DELETE for `/students`, plus `/ask` |
| `python -m pytest -q` | All tests pass (one harmless `httpx` deprecation warning may appear) |

Example: creating a student returns `201` with the saved record:
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
The browser message `GET /favicon.ico 404` in the server log is harmless. See **SAMPLE_OUTPUT.md** for the full output of every endpoint, including error cases (409, 422, 404, 503).

---

## 3. Using the API

Open **http://127.0.0.1:8000** to use the dashboard directly. No login or registration is required. Student APIs are also accessible without credentials.

> **Access warning:** This project has no authentication. Anyone who can reach the server can view, create, edit, or delete student records. Run it only on a trusted local network or add an appropriate access-control layer before deployment.

Use the search box and course filter to narrow records; change sorting and page size as needed. Export the current filtered list with **Export CSV**. The theme toggle switches between light and dark mode and remembers your choice in that browser.

Use **Import CSV** to download a template or preview an existing CSV before importing. Files can contain up to 500 students (5 MB); each row is validated individually, and duplicate or invalid records are listed without interrupting valid rows. Upcoming birthdays are highlighted for the next 30 days and open the student's profile when selected.

Use **Add student** to create a record, or the row actions to view a student profile, edit, or delete one. Profile quick-view shows age and available contact/enrollment details, with direct email and phone links. The dashboard communicates with the API and reports validation errors such as duplicate email addresses. The API remains available at `/students`; interactive API documentation is at `/docs`.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/students` | Create a student |
| GET | `/students` | List / filter students |
| GET | `/students/{student_id}` | View a student |
| PUT | `/students/{student_id}` | Replace all details |
| PATCH | `/students/{student_id}` | Update some details |
| DELETE | `/students/{student_id}` | Delete a student |
| POST | `/ask` | (Optional) Ask a question using Ollama |

**Filters:** `/students?course=computer`, `/students?name=aar`, `/students?born_after=2005-01-01&limit=10`

### Test in the browser (easiest)
1. Open `/docs`.
2. Click an endpoint, click **Try it out**, fill in the values, click **Execute**.

### Test with curl (Mac / Linux / Git Bash)
```bash
# Create
curl -X POST http://127.0.0.1:8000/students -H "Content-Type: application/json" \
  -d '{"name":"Test Student","date_of_birth":"2004-05-17","email":"test@example.com","phone":"+91 98765 43210","course":"Computer Science"}'

# List all
curl http://127.0.0.1:8000/students

# View one
curl http://127.0.0.1:8000/students/1

# Partial update
curl -X PATCH http://127.0.0.1:8000/students/1 -H "Content-Type: application/json" -d '{"course":"AI and Data Science"}'

# Delete
curl -X DELETE http://127.0.0.1:8000/students/1
```

### Test with PowerShell (Windows)
```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/students -ContentType "application/json" `
  -Body '{"name":"Test Student","date_of_birth":"2004-05-17","email":"test@example.com"}'
Invoke-RestMethod http://127.0.0.1:8000/students
```

### Student fields
| Field | Required | Notes |
|---|---|---|
| name | Yes | 1 to 100 characters |
| date_of_birth | Yes | `YYYY-MM-DD`, must be in the past |
| email | One of email/phone | Must be valid and unique |
| phone | One of email/phone | 7 to 19 characters (digits, spaces, hyphens), optional leading + |
| course, address, enrollment_date | No | |

---

## 4. Optional: AI questions with Ollama
1. Install Ollama from https://ollama.com.
2. Download the model: `ollama pull llama3.2:1b`
3. Make sure Ollama is running (`ollama serve` if needed).
4. Ask a question:
```bash
curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" -d '{"question":"List students born after 2005"}'
```
How it works: backend code detects the year or course in the question, fetches matching records with normal queries, adds exact totals, and sends only that context to the model. The response lists `records_used` so you can verify the answer. If Ollama is not running, `/ask` returns `503` and the rest of the API still works.

## 5. Project structure
```
students-crud/
├── app/
│   ├── main.py          # FastAPI app, creates tables on startup
│   ├── static/
│   │   └── index.html   # Responsive dashboard (HTML, CSS, and JavaScript)
│   ├── database.py      # SQLite engine and session
│   ├── models.py        # Database table
│   ├── schemas.py       # Validation rules (Pydantic)
│   ├── crud.py          # Database operations
│   ├── ai.py            # Ollama logic (optional)
│   └── routers/
│       ├── students.py  # /students endpoints
│       └── ai.py        # /ask endpoint
├── tests/test_students.py
├── seed.py              # Dummy data
├── SAMPLE_OUTPUT.md     # Real example outputs
├── requirements.txt
└── README.md
```

## 6. Configuration (optional environment variables)
| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./students.db` | Database location |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server address |
| `OLLAMA_MODEL` | `llama3.2:1b` | Model name |
| `AUTH_COOKIE_SECURE` | `false` | Set to `true` when serving over HTTPS outside local development |

## 7. Troubleshooting
| Problem | Fix |
|---|---|
| `python` not recognized | Install Python from python.org and tick "Add Python to PATH". On Mac/Linux use `python3`. |
| `No module named 'app'` or `Could not import module` | Run the command from the project root (the folder containing `app/`). |
| `No module named fastapi` (or another package) | Activate the virtual environment, then run `pip install -r requirements.txt` again. |
| `email-validator is not installed` | Reinstall with `pip install -r requirements.txt`. |
| `uvicorn` not recognized | Always use `python -m uvicorn app.main:app --reload`. |
| Syntax error mentioning `list[...]` or `|` | Your Python is too old. Install Python 3.10+. |
| Port 8000 already in use | Add `--port 8001` and open `http://127.0.0.1:8001/docs`. |
| `409 Conflict` when creating | That email already exists. Use a different email. |
| `503` from `/ask` | Ollama is not running or the model is not downloaded. |
| Session cookie is rejected in production | Serve the app over HTTPS and set `AUTH_COOKIE_SECURE=true`. |
| Table or column errors after editing models | Stop the server, delete `students.db`, start again (and re-run `seed.py`). |

## 8. Push to GitHub (submission)
```bash
git init
git add .
git commit -m "Students CRUD API with FastAPI and SQLite"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```
The `.gitignore` already excludes `.venv/`, `students.db` and cache files. Do not commit passwords, secrets or real student data. Add screenshots of the `/docs` page to this README if you can.
