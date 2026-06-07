from typing import List, Optional

from fastapi import HTTPException

from src.curs_bnr.backend.database import read_exchange_rates
from src.curs_bnr.backend.schemas import RateResponse


def fetch_rates(currency_code: str = "USD", limit: Optional[int] = None) -> List[RateResponse]:
    """Preia lista de cursuri valutare din baza de date."""
    try:
        rates = read_exchange_rates()
    except RuntimeError as error:
        raise HTTPException(
            status_code=500,
            detail=f"Eroare SQL la citirea cursurilor: {error}",
        )

    filtered = [
        rate for rate in rates if rate["currency_code"].upper() == currency_code.upper()
    ]
    if limit is not None and limit > 0:
        filtered = filtered[:limit]
    return [RateResponse(**rate) for rate in filtered]
