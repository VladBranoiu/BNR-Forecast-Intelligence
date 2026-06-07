from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from src.curs_bnr.backend.database import initialize_database
from src.curs_bnr.backend.schemas import (
    ForecastLatestResponse,
    RateResponse,
    RetrainRequest,
    RetrainResponse,
    RunResponse,
    ScrapeRequest,
    ScrapeResponse,
)
from src.curs_bnr.backend.services.forecast_service import fetch_latest_forecast
from src.curs_bnr.backend.services.rates_service import fetch_rates
from src.curs_bnr.backend.services.scraper_service import trigger_scraper
from src.curs_bnr.backend.services.training_service import fetch_training_runs, perform_retraining

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan handler pentru FastAPI: inițializează DB la startup."""
    initialize_database()
    yield


app = FastAPI(title="Prognoza curs valutar BNR", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/", response_model=Dict[str, str])
def root() -> Dict[str, str]:
    """Verificare de stare pentru backend."""
    return {"message": "Backend BNR rulează"}


@app.get("/api/rates", response_model=List[RateResponse])
def read_rates(
    currency_code: str = "USD",
    limit: Optional[int] = Query(None, ge=1),
) -> List[RateResponse]:
    """Returnează lista cursurilor valutare din baza de date."""
    rates = fetch_rates(currency_code=currency_code, limit=limit)
    return rates


@app.get("/api/forecast/latest", response_model=ForecastLatestResponse)
def read_latest_forecast(
    currency_code: str = Query("USD"),
) -> ForecastLatestResponse:
    """Returnează ultima rulare de forecast cu toate prognozele ei pentru o monedă."""
    forecast = fetch_latest_forecast(currency_code=currency_code)
    if forecast is None:
        raise HTTPException(
            status_code=404,
            detail=f"Nu există nicio prognoză salvată în baza de date pentru {currency_code}.",
        )
    return forecast


@app.get("/api/runs", response_model=List[RunResponse])
def read_runs(limit: int = Query(10, ge=1, le=100)) -> List[RunResponse]:
    """Returnează lista rulărilor de antrenare recente."""
    runs = fetch_training_runs(limit=limit)
    if not runs:
        raise HTTPException(
            status_code=404,
            detail="Nu s-au găsit rulări de antrenare în baza de date.",
        )
    return runs


@app.post("/api/scrape", response_model=ScrapeResponse)
def post_scrape(request: ScrapeRequest) -> ScrapeResponse:
    """Declanșează scraperul BNR și salvează rezultatele în baza de date."""
    result = trigger_scraper(
        currency_code=request.currency_code,
        start_date=request.start_date,
    )
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return ScrapeResponse(**result)


@app.post("/api/retrain", response_model=RetrainResponse)
def post_retrain(request: RetrainRequest) -> RetrainResponse:
    """Pornește un ciclu de reantrenare a modelelor folosind datele disponibile."""
    result = perform_retraining(
        currency_code=request.currency_code,
        horizon=request.forecast_horizon,
    )
    if not result.get("success", False):
        raise HTTPException(status_code=500, detail=result.get("message", "Eroare la reantrenare."))
    return RetrainResponse(**result)
