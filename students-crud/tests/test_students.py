import asyncio
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from app import ai
from app import main as main_module
from app.database import Base, get_db
from app.main import app
from app.models import Student


@pytest.fixture()
def session_factory(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture()
def anonymous_client(session_factory):
    def override():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def client(anonymous_client):
    return anonymous_client


def make(name="Test User", dob="2004-05-17", email="test@example.com", **extra):
    return {"name": name, "date_of_birth": dob, "email": email, **extra}


def test_auth_routes_are_removed_and_student_api_is_open(client):
    assert client.get("/auth/status").status_code == 404
    assert client.post("/auth/login").status_code == 404
    assert client.post("/auth/register").status_code == 404
    assert client.get("/students").status_code == 200
    assert client.post("/students", json=make()).status_code == 201


def test_startup_removes_legacy_auth_tables(monkeypatch):
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, password_hash TEXT)"))
        connection.execute(text("CREATE TABLE auth_sessions (token_hash TEXT PRIMARY KEY)"))
        connection.execute(text("CREATE TABLE bootstrap_admin (id INTEGER PRIMARY KEY)"))
    monkeypatch.setattr(main_module, "engine", engine)

    async def run_lifespan():
        async with main_module.app.router.lifespan_context(main_module.app):
            pass

    asyncio.run(run_lifespan())
    assert inspect(engine).get_table_names() == ["students"]
    engine.dispose()


def test_homepage_serves_student_dashboard(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    for feature in (
        "Student directory",
        "theme-toggle",
        "course-filter",
        "export-button",
        "import-button",
        "birthday-panel",
        "profile-dialog",
        "pagination",
        "Student workspace",
    ):
        assert feature in response.text
    for removed_feature in ("login-form", "setup-form", "registration-button", "logout-button"):
        assert removed_feature not in response.text


def test_create_and_get(client):
    r = client.post("/students", json=make(course="CS", phone="+91 99999 99999"))
    assert r.status_code == 201
    sid = r.json()["id"]
    got = client.get(f"/students/{sid}")
    assert got.status_code == 200
    assert got.json()["email"] == "test@example.com"


def test_list_and_filter(client):
    client.post("/students", json=make("Alice", "2004-01-01", "a@example.com", course="CS"))
    client.post("/students", json=make("Bob", "2006-06-06", "b@example.com", course="IT"))
    assert len(client.get("/students").json()) == 2
    assert [s["name"] for s in client.get("/students?course=it").json()] == ["Bob"]
    assert [s["name"] for s in client.get("/students?name=ali").json()] == ["Alice"]
    assert [s["name"] for s in client.get("/students?born_after=2005-01-01").json()] == ["Bob"]


def test_put_replaces(client):
    sid = client.post("/students", json=make()).json()["id"]
    r = client.put(f"/students/{sid}", json=make("New Name", "2003-03-03", "new@example.com"))
    assert r.status_code == 200 and r.json()["name"] == "New Name"


def test_patch_partial(client):
    sid = client.post("/students", json=make(course="CS")).json()["id"]
    r = client.patch(f"/students/{sid}", json={"course": "AI"})
    assert r.status_code == 200
    assert r.json()["course"] == "AI" and r.json()["name"] == "Test User"


def test_patch_cannot_remove_all_contacts(client):
    sid = client.post("/students", json=make()).json()["id"]
    assert client.patch(f"/students/{sid}", json={"email": None}).status_code == 422


def test_delete(client):
    sid = client.post("/students", json=make()).json()["id"]
    assert client.delete(f"/students/{sid}").status_code == 204
    assert client.get(f"/students/{sid}").status_code == 404


def test_missing_record_404(client):
    assert client.get("/students/999").status_code == 404
    assert client.patch("/students/999", json={"name": "x"}).status_code == 404
    assert client.delete("/students/999").status_code == 404


def test_duplicate_email_409(client):
    client.post("/students", json=make())
    assert client.post("/students", json=make("Other")).status_code == 409


@pytest.mark.parametrize("bad", [
    make(email="not-an-email"),
    make(dob="2999-01-01"),
    make(name="   "),
    {"name": "No Contact", "date_of_birth": "2004-01-01"},
    make(phone="abc"),
])
def test_validation_422(client, bad):
    assert client.post("/students", json=bad).status_code == 422


def test_ai_context_is_grounded(session_factory):
    with session_factory() as db:
        db.add_all([
            Student(name="A", date_of_birth=date(2004, 1, 1), email="a@example.com", course="CS"),
            Student(name="B", date_of_birth=date(2006, 1, 1), email="b@example.com", course="IT"),
            Student(name="C", date_of_birth=date(2007, 1, 1), email="c@example.com", course="IT"),
        ])
        db.commit()
        records, total = ai.select_records(db, "List students born after 2005")
        assert total == 3 and [s.name for s in records] == ["B", "C"]
        records, _ = ai.select_records(db, "Who is in IT?")
        assert [s.name for s in records] == ["B", "C"]
        assert "TOTAL students in database: 3" in ai.build_context(records, total)


def test_ask_returns_503_when_ollama_down(client, monkeypatch):
    def boom(*a, **k):
        raise ai.OllamaUnavailable("down")

    monkeypatch.setattr(ai, "ask_ollama", boom)
    assert client.post("/ask", json={"question": "How many students are there?"}).status_code == 503
