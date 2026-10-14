import sys
import os
import sqlite3

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

import pytest

from app import app, init_db


@pytest.fixture
def client(tmp_path, monkeypatch):

    db_path = tmp_path / "test.db"

    def get_test_db():

        conn = sqlite3.connect(str(db_path))

        conn.row_factory = sqlite3.Row

        return conn

    monkeypatch.setattr(
        "app.get_db",
        get_test_db
    )

    init_db()

    app.config["TESTING"] = True

    with app.test_client() as client:

        yield client


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

def test_home(client):

    response = client.get("/")

    assert response.status_code == 200


# --------------------------------------------------
# LOGIN PAGE
# --------------------------------------------------

def test_login_page(client):

    response = client.get("/login")

    assert response.status_code == 200


# --------------------------------------------------
# REGISTER PAGE
# --------------------------------------------------

def test_register_page(client):

    response = client.get("/register")

    assert response.status_code == 200


# --------------------------------------------------
# STUDENT COMPLAINT
# --------------------------------------------------

def test_complaint_requires_login(client):

    response = client.get("/complaint")

    assert response.status_code == 302


# --------------------------------------------------
# STUDENT DASHBOARD
# --------------------------------------------------

def test_dashboard_requires_login(client):

    response = client.get("/dashboard")

    assert response.status_code == 302


# --------------------------------------------------
# ADMIN ACCESS
# --------------------------------------------------

def test_admin_requires_login(client):

    response = client.get("/admin")

    assert response.status_code == 200


# --------------------------------------------------
# MAINTENANCE ACCESS
# --------------------------------------------------

def test_maintenance_requires_login(client):

    response = client.get("/maintenance")

    assert response.status_code == 200


# --------------------------------------------------
# TUTOR ACCESS
# --------------------------------------------------

def test_tutor_requires_login(client):

    response = client.get("/tutor")

    assert response.status_code == 200


# --------------------------------------------------
# HOD ACCESS
# --------------------------------------------------

def test_hod_requires_login(client):

    response = client.get("/hod")

    assert response.status_code == 200