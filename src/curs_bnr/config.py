"""Configurație generală pentru aplicația de prognoză curs valutar BNR."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BASE_DIR
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
DATABASE_PATH = DATA_DIR / "curs_bnr.sqlite"
BACKEND_URL = "http://localhost:7772"
API_HOST = "127.0.0.1"
API_PORT = 7772

SCRAPER_SOURCE = "https://www.bnr.ro/nbrfxrates.xml"

# Parametri generali pentru componenta de antrenare
MODEL_VERSION = "v1"
FORECAST_HORIZON = 30

# Structuri dedicate instrumentelor locale
TOOL_REGISTRY = {
    "latest_forecast": "/api/forecast/latest",
    "latest_rates": "/api/rates",
}
