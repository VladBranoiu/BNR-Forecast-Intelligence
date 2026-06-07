import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.curs_bnr.config import DATA_DIR, DATABASE_PATH


def _ensure_data_directory() -> None:
    """Creează directorul de date dacă nu există."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _has_column(connection: sqlite3.Connection, table_name: str, column_name: str) -> bool:
    cursor = connection.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    return any(row["name"] == column_name for row in cursor.fetchall())


def _add_column_if_missing(
    connection: sqlite3.Connection,
    table_name: str,
    column_name: str,
    column_definition: str,
) -> None:
    if not _has_column(connection, table_name, column_name):
        cursor = connection.cursor()
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_definition}")
        connection.commit()


def _migrate_schema(connection: sqlite3.Connection) -> None:
    """Adaugă coloane noi la tabelele existente dacă este necesar."""
    _add_column_if_missing(
        connection,
        "training_runs",
        "currency_code",
        "currency_code TEXT NOT NULL DEFAULT 'USD'",
    )
    _add_column_if_missing(
        connection,
        "forecasts",
        "currency_code",
        "currency_code TEXT NOT NULL DEFAULT 'USD'",
    )


def _initialize_schema(connection: sqlite3.Connection) -> None:
    """Creează tabelele și indexurile necesare pentru baza de date."""
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS exchange_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            currency_code TEXT NOT NULL,
            rate_date TEXT NOT NULL,
            value REAL NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_exchange_rates_currency_date
        ON exchange_rates(currency_code, rate_date)
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS training_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at TEXT NOT NULL,
            method TEXT NOT NULL,
            winner_model TEXT NOT NULL,
            winner_mae REAL NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS model_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            model_name TEXT NOT NULL,
            parameters_json TEXT NOT NULL,
            mae REAL NOT NULL,
            rmse REAL NOT NULL,
            mape REAL NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(run_id) REFERENCES training_runs(id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            model_name TEXT NOT NULL,
            forecast_date TEXT NOT NULL,
            predicted_value REAL NOT NULL,
            lower_bound REAL NOT NULL,
            upper_bound REAL NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(run_id) REFERENCES training_runs(id)
        )
        """
    )
    connection.commit()


def _get_connection() -> sqlite3.Connection:
    """Deschide o conexiune SQLite către fișierul bazei de date."""
    _ensure_data_directory()
    connection = sqlite3.connect(str(DATABASE_PATH))
    connection.row_factory = sqlite3.Row
    _initialize_schema(connection)
    _migrate_schema(connection)
    return connection


def initialize_database() -> None:
    """Inițializează baza de date și crează tabelele necesare."""
    connection = _get_connection()
    connection.close()


def insert_exchange_rate(currency_code: str, rate_date: str, value: float) -> int:
    """Inserează un curs valutar în tabelul exchange_rates, evitând duplicatele."""
    connection = _get_connection()
    cursor = connection.cursor()
    created_at = datetime.now(timezone.utc).isoformat()
    cursor.execute(
        """
        INSERT OR IGNORE INTO exchange_rates (currency_code, rate_date, value, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (currency_code, rate_date, value, created_at),
    )
    connection.commit()
    row_id = cursor.lastrowid
    connection.close()
    return row_id


def read_exchange_rates() -> List[Dict[str, Any]]:
    """Returnează toate cursurile valutare din baza de date."""
    connection = _get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT id, currency_code, rate_date, value, created_at
            FROM exchange_rates
            ORDER BY rate_date DESC, id DESC
            """
        )
        rows = cursor.fetchall()
    except sqlite3.DatabaseError as error:
        connection.close()
        raise RuntimeError(
            f"Eroare SQL la citirea cursurilor: {error}"
        ) from error
    connection.close()
    return [dict(row) for row in rows]


def read_training_runs(limit: int = 10) -> List[Dict[str, Any]]:
    """Returnează lista rulărilor de antrenare recente."""
    connection = _get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT id, run_at, method, winner_model, winner_mae, notes, created_at
        FROM training_runs
        ORDER BY run_at DESC, id DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    connection.close()
    return [dict(row) for row in rows]


def read_model_results_by_run_id(run_id: int) -> List[Dict[str, Any]]:
    """Returnează lista rezultatelor de modele asociate unei rulări de training."""
    connection = _get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT id, run_id, model_name, parameters_json, mae, rmse, mape, created_at
        FROM model_results
        WHERE run_id = ?
        ORDER BY mae ASC, id ASC
        """,
        (run_id,),
    )
    rows = cursor.fetchall()
    connection.close()
    return [dict(row) for row in rows]


def insert_training_run(
    run_at: str,
    method: str,
    winner_model: str,
    winner_mae: float,
    currency_code: str = "USD",
    notes: Optional[str] = None,
) -> int:
    """Inserează un rezultat de rulare de antrenare în tabelul training_runs."""
    connection = _get_connection()
    cursor = connection.cursor()
    created_at = datetime.now(timezone.utc).isoformat()
    cursor.execute(
        """
        INSERT INTO training_runs (run_at, method, winner_model, winner_mae, currency_code, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (run_at, method, winner_model, winner_mae, currency_code, notes, created_at),
    )
    connection.commit()
    row_id = cursor.lastrowid
    connection.close()
    return row_id


def insert_model_result(
    run_id: int,
    model_name: str,
    parameters_json: str,
    mae: float,
    rmse: float,
    mape: float,
) -> int:
    """Inserează un rezultat de evaluare a unui model în tabelul model_results."""
    connection = _get_connection()
    cursor = connection.cursor()
    created_at = datetime.now(timezone.utc).isoformat()
    cursor.execute(
        """
        INSERT INTO model_results (run_id, model_name, parameters_json, mae, rmse, mape, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (run_id, model_name, parameters_json, mae, rmse, mape, created_at),
    )
    connection.commit()
    row_id = cursor.lastrowid
    connection.close()
    return row_id


def insert_forecast(
    run_id: int,
    model_name: str,
    forecast_date: str,
    predicted_value: float,
    lower_bound: float,
    upper_bound: float,
    currency_code: str = "USD",
) -> int:
    """Inserează o prognoză în tabelul forecasts."""
    connection = _get_connection()
    cursor = connection.cursor()
    created_at = datetime.now(timezone.utc).isoformat()
    cursor.execute(
        """
        INSERT INTO forecasts (
            run_id,
            model_name,
            forecast_date,
            predicted_value,
            lower_bound,
            upper_bound,
            currency_code,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (run_id, model_name, forecast_date, predicted_value, lower_bound, upper_bound, currency_code, created_at),
    )
    connection.commit()
    row_id = cursor.lastrowid
    connection.close()
    return row_id


def read_latest_forecast() -> Optional[Dict[str, Any]]:
    """Returnează ultima prognoză adăugată în baza de date."""
    connection = _get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT id, run_id, model_name, forecast_date, predicted_value,
               lower_bound, upper_bound, created_at
        FROM forecasts
        ORDER BY forecast_date DESC, id DESC
        LIMIT 1
        """
    )
    row = cursor.fetchone()
    connection.close()
    return dict(row) if row else None


def read_latest_forecast_run(currency_code: str = "USD") -> Optional[Dict[str, Any]]:
    """Returnează toate prognozele ultimei rulări de antrenare pentru o monedă."""
    latest_run = read_latest_training_run(currency_code=currency_code)
    if latest_run is None:
        return None

    connection = _get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT forecast_date, predicted_value, lower_bound, upper_bound
        FROM forecasts
        WHERE run_id = ?
        ORDER BY forecast_date ASC, id ASC
        """,
        (latest_run["id"],),
    )
    rows = cursor.fetchall()
    connection.close()

    if not rows:
        return None

    return {
        "run_id": latest_run["id"],
        "winner_model": latest_run["winner_model"],
        "winner_mae": latest_run["winner_mae"],
        "forecasts": [dict(row) for row in rows],
    }


def read_latest_training_run(currency_code: str = "USD") -> Optional[Dict[str, Any]]:
    """Returnează ultima rulare de antrenare înregistrată pentru o monedă."""
    connection = _get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT id, run_at, method, winner_model, winner_mae, notes, created_at
        FROM training_runs
        WHERE currency_code = ?
        ORDER BY run_at DESC, id DESC
        LIMIT 1
        """,
        (currency_code,),
    )
    row = cursor.fetchone()
    connection.close()
    return dict(row) if row else None
