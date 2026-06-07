from typing import Optional

from pydantic import BaseModel


class ExchangeRateResponse(BaseModel):
    id: int
    currency_code: str
    rate_date: str
    value: float
    created_at: str


class ForecastResponse(BaseModel):
    id: int
    run_id: int
    model_name: str
    forecast_date: str
    predicted_value: float
    lower_bound: float
    upper_bound: float
    created_at: str


class ForecastPoint(BaseModel):
    forecast_date: str
    predicted_value: float
    lower_bound: float
    upper_bound: float


class ForecastLatestResponse(BaseModel):
    run_id: int
    winner_model: str
    winner_mae: float
    forecasts: list[ForecastPoint]


class ScrapeRequest(BaseModel):
    currency_code: str = "USD"
    start_date: str = "22/02/2020"


class ScrapeResponse(BaseModel):
    success: bool
    currency_code: str
    start_date: str
    records_count: int
    message: str

class ModelResultResponse(BaseModel):
    id: int
    run_id: int
    model_name: str
    parameters_json: str
    mae: float
    rmse: float
    mape: float
    created_at: str


class TrainingRunResponse(BaseModel):
    id: int
    run_at: str
    method: str
    winner_model: str
    winner_mae: float
    winner_rmse: Optional[float] = None
    winner_mape: Optional[float] = None
    results: list[ModelResultResponse] = []
    notes: Optional[str] = None
    created_at: str


class RetrainRequest(BaseModel):
    currency_code: str = "USD"
    forecast_horizon: int = 7


class RetrainResponse(BaseModel):
    success: bool
    run_id: int | None = None
    winner_model: str | None = None
    winner_mae: float | None = None
    forecast_horizon: int | None = None
    forecast_records: int | None = None
    message: str


# Compatibilitate cu endpoint-urile existente
RateResponse = ExchangeRateResponse
RunResponse = TrainingRunResponse
