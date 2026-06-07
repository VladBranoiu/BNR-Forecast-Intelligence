import sqlite3

from src.curs_bnr.backend import database as db


def test_initialize_database_creates_tables(temp_database_path):
    """Verifică că inițializarea bazei de date creează tabelele necesare."""
    connection = sqlite3.connect(temp_database_path)
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    connection.close()

    assert {"exchange_rates", "training_runs", "model_results", "forecasts"}.issubset(tables)


def test_insert_exchange_rate_and_read_returns_rate(temp_database_path):
    """Inserează un curs și verifică că poate fi citit din baza de date."""
    row_id = db.insert_exchange_rate("USD", "2026-06-07", 4.5)
    rates = db.read_exchange_rates()

    assert row_id > 0
    assert len(rates) == 1
    assert rates[0]["currency_code"] == "USD"
    assert rates[0]["rate_date"] == "2026-06-07"
    assert rates[0]["value"] == 4.5


def test_read_exchange_rates_returns_list(temp_database_path):
    """Verifică că citirea cursurilor returnează o listă de dicționare."""
    db.insert_exchange_rate("USD", "2026-06-07", 4.5)
    result = db.read_exchange_rates()

    assert isinstance(result, list)
    assert all(isinstance(item, dict) for item in result)


def test_insert_duplicate_exchange_rate_is_ignored(temp_database_path):
    """Verifică că duplicatele pentru aceeași valută și dată nu produc eroare."""
    first_id = db.insert_exchange_rate("USD", "2026-06-07", 4.5)
    second_id = db.insert_exchange_rate("USD", "2026-06-07", 4.5)
    rates = db.read_exchange_rates()

    assert first_id > 0
    assert second_id == 0
    assert len(rates) == 1


def test_read_latest_forecast_returns_none_when_empty(temp_database_path):
    """Verifică că nu există prognoză dacă tabelul este gol."""
    latest_forecast = db.read_latest_forecast()

    assert latest_forecast is None
