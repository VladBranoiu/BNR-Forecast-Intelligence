import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.curs_bnr.backend import database as backend_database
from src.curs_bnr.backend.main import app


@pytest.fixture
def temp_database_path(tmp_path, monkeypatch):
    """Configurează o bază de date SQLite temporară pentru teste."""
    db_path = tmp_path / "curs_bnr_test.sqlite"
    data_dir = tmp_path
    monkeypatch.setattr(backend_database, "DATABASE_PATH", db_path)
    monkeypatch.setattr(backend_database, "DATA_DIR", data_dir)
    backend_database.initialize_database()
    return db_path


@pytest.fixture
def client(temp_database_path):
    """Furnizează un TestClient pentru aplicația FastAPI cu bază temporară."""
    with TestClient(app) as client_instance:
        yield client_instance
