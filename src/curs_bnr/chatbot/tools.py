"""Tool-uri locale pentru chatbot — apeluri către backend.

Aceste funcții comunică exclusiv prin API-ul FastAPI (fără acces direct la SQLite
și fără integrare LLM). Toate funcțiile returnează un dicționar standard:

{
  "success": bool,
  "data": Any,
  "message": str,
}
"""
from typing import Any, Dict, Optional
import os

import requests
from dotenv import load_dotenv

load_dotenv()

# Backend URL configurabil via .env
BACKEND_URL = os.getenv("BNR_BACKEND_URL", "http://localhost:7772")
TIMEOUT = 8


def _safe_get(path: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
    """Efectuează un GET cu timeout și aruncă excepții requests standard.

    Funcție internă pentru reuse.
    """
    return requests.get(f"{BACKEND_URL}{path}", params=params or {}, timeout=TIMEOUT)


def _safe_post(path: str, json_payload: Optional[Dict[str, Any]] = None) -> requests.Response:
    """Efectuează un POST cu timeout și aruncă excepții requests standard."""
    return requests.post(f"{BACKEND_URL}{path}", json=json_payload or {}, timeout=TIMEOUT)


def get_latest_exchange_rate(currency_code: str = "USD") -> Dict[str, Any]:
    """Returnează cel mai recent curs pentru `currency_code`.

    Apelează `GET /api/rates?currency_code=...` și returnează primul element
    din listă (dacă există).
    """
    try:
        resp = _safe_get("/api/rates", params={"currency_code": currency_code})
    except requests.RequestException as err:
        return {"success": False, "data": None, "message": f"Eroare rețea: {err}"}

    if resp.status_code != 200:
        return {"success": False, "data": None, "message": f"Eroare backend: {resp.status_code}"}

    try:
        data = resp.json()
    except ValueError:
        return {"success": False, "data": None, "message": "Răspuns invalid JSON"}

    if not isinstance(data, list) or not data:
        return {"success": False, "data": None, "message": "Nu există date pentru această valută."}

    latest = data[0]
    return {"success": True, "data": latest, "message": "Curs preluat cu succes."}


def get_forecast_summary() -> Dict[str, Any]:
    """Returnează ultima prognoză salvată (apelează `GET /api/forecast/latest`)."""
    try:
        resp = _safe_get("/api/forecast/latest")
    except requests.RequestException as err:
        return {"success": False, "data": None, "message": f"Eroare rețea: {err}"}

    if resp.status_code == 404:
        return {"success": False, "data": None, "message": "Nu există prognoză disponibilă."}
    if resp.status_code != 200:
        return {"success": False, "data": None, "message": f"Eroare backend: {resp.status_code}"}

    try:
        data = resp.json()
    except ValueError:
        return {"success": False, "data": None, "message": "Răspuns invalid JSON"}

    return {"success": True, "data": data, "message": "Prognoză obținută."}


def get_model_metrics() -> Dict[str, Any]:
    """Returnează metrica (winner model + MAE) din ultima rulare `GET /api/runs?limit=1`.

    Dacă nu există rulări, se întoarce success=False.
    """
    try:
        resp = _safe_get("/api/runs", params={"limit": 1})
    except requests.RequestException as err:
        return {"success": False, "data": None, "message": f"Eroare rețea: {err}"}

    if resp.status_code != 200:
        return {"success": False, "data": None, "message": f"Eroare backend: {resp.status_code}"}

    try:
        data = resp.json()
    except ValueError:
        return {"success": False, "data": None, "message": "Răspuns invalid JSON"}

    if not isinstance(data, list) or not data:
        return {"success": False, "data": None, "message": "Nu există rulări înregistrate."}

    run = data[0]
    metrics = {"winner_model": run.get("winner_model"), "winner_mae": run.get("winner_mae"), "run_id": run.get("id")}
    return {"success": True, "data": metrics, "message": "Metrici obținute."}


def trigger_scrape(currency_code: str = "USD", start_date: str = "22/02/2020") -> Dict[str, Any]:
    """Declanșează scrapingul prin API (POST /api/scrape)."""
    payload = {"currency_code": currency_code, "start_date": start_date}
    try:
        resp = _safe_post("/api/scrape", json_payload=payload)
    except requests.RequestException as err:
        return {"success": False, "data": None, "message": f"Eroare rețea la scraping: {err}"}

    if resp.status_code != 200:
        return {"success": False, "data": None, "message": f"Eroare backend: {resp.status_code}",}

    try:
        result = resp.json()
    except ValueError:
        return {"success": False, "data": None, "message": "Răspuns invalid JSON la scraping"}

    return {"success": result.get("success", False), "data": result, "message": result.get("message", "")} 


def trigger_retraining(currency_code: str = "USD") -> Dict[str, Any]:
    """Pornește reantrenarea prin API (POST /api/retrain)."""
    payload = {"currency_code": currency_code, "forecast_horizon": 7}
    try:
        resp = _safe_post("/api/retrain", json_payload=payload)
    except requests.RequestException as err:
        return {"success": False, "data": None, "message": f"Eroare rețea la reantrenare: {err}"}

    if resp.status_code != 200:
        return {"success": False, "data": None, "message": f"Eroare backend: {resp.status_code}"}

    try:
        result = resp.json()
    except ValueError:
        return {"success": False, "data": None, "message": "Răspuns invalid JSON la reantrenare"}

    return {"success": result.get("success", False), "data": result, "message": result.get("message", "")} 
from typing import Any, Dict


def get_latest_forecast_tool() -> Dict[str, Any]:
    """Funcție placeholder pentru aducerea ultimei prognoze."""
    return {"forecast": None}


def get_current_rates_tool() -> Dict[str, Any]:
    """Funcție placeholder pentru aducerea cursurilor curente."""
    return {"rates": []}


def trigger_scrape_tool() -> Dict[str, str]:
    """Funcție placeholder pentru declanșarea scraperului BNR."""
    return {"status": "scrape_requested"}
