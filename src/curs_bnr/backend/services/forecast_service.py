from typing import Optional

from src.curs_bnr.backend.database import read_latest_forecast_run
from src.curs_bnr.backend.schemas import ForecastLatestResponse


def fetch_latest_forecast(currency_code: str = "USD") -> Optional[ForecastLatestResponse]:
    """Returnează toate prognozele ultimei rulări disponibile pentru o monedă."""
    row = read_latest_forecast_run(currency_code=currency_code)
    if row is None:
        return None
    return ForecastLatestResponse(**row)
