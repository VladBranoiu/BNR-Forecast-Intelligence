from typing import Any, Dict, List

from src.curs_bnr.backend.database import insert_exchange_rate
from src.curs_bnr.scraper.bnr_scraper import fetch_bnr_data


def trigger_scraper(
    currency_code: str = "USD",
    start_date: str = "22/02/2020",
) -> Dict[str, Any]:
    """Rulează scraperul BNR și salvează datele în baza de date SQLite."""
    result: Dict[str, Any] = {
        "success": False,
        "currency_code": currency_code,
        "start_date": start_date,
        "records_count": 0,
        "message": "",
    }

    try:
        rates: List[Dict[str, Any]] = fetch_bnr_data(currency_code, start_date)
        for rate in rates:
            insert_exchange_rate(rate["currency_code"], rate["rate_date"], rate["value"])

        result["success"] = True
        result["records_count"] = len(rates)
        result["message"] = "Datele BNR au fost salvate cu succes."
    except Exception as exc:
        result["message"] = str(exc)

    return result
