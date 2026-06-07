from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from joblib import dump
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX

from src.curs_bnr.backend.database import (
    insert_forecast,
    insert_model_result,
    insert_training_run,
    read_exchange_rates,
)
from src.curs_bnr.config import MODELS_DIR
from src.curs_bnr.ml.evaluate_models import evaluate_models
from src.curs_bnr.ml.forecast import generate_forecast

MODEL_FILENAME = MODELS_DIR / "best_model.pkl"


def _ensure_models_directory() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)


def _load_exchange_rate_series(currency_code: str = "USD") -> pd.Series:
    records = read_exchange_rates()
    filtered = [row for row in records if row["currency_code"].upper() == currency_code.upper()]
    if not filtered:
        raise ValueError(f"Nu s-au găsit date pentru moneda {currency_code}.")
    df = pd.DataFrame(filtered)
    parsed_dates = pd.to_datetime(df["rate_date"], format="%Y-%m-%d", errors="coerce")
    if parsed_dates.isna().any():
        fallback = pd.to_datetime(
            df.loc[parsed_dates.isna(), "rate_date"],
            dayfirst=True,
            errors="coerce",
        )
        parsed_dates.loc[parsed_dates.isna()] = fallback
    df["rate_date"] = parsed_dates
    df = df.dropna(subset=["rate_date"]).sort_values("rate_date")
    if df.empty:
        raise ValueError("Datele din baza de date nu sunt valide pentru antrenare.")
    return pd.Series(df["value"].values, index=df["rate_date"])


def _train_test_split(series: pd.Series, test_size: int = 14) -> tuple[pd.Series, pd.Series]:
    if len(series) < test_size + 10:
        raise ValueError(
            "Nu există suficiente date pentru antrenare și test. "
            "Colectați mai multe date înainte de proces."
        )
    test_size = min(test_size, max(7, len(series) // 4))
    train = series.iloc[:-test_size]
    test = series.iloc[-test_size:]
    return train, test


def _build_forecast_dates(last_date: pd.Timestamp, horizon: int) -> List[str]:
    dates = pd.bdate_range(start=last_date + pd.Timedelta(days=1), periods=horizon)
    return [date.date().isoformat() for date in dates]


def _fit_arima(train_series: pd.Series) -> Any:
    return ARIMA(train_series, order=(2, 1, 2)).fit()


def _fit_sarimax(train_series: pd.Series) -> Any:
    return SARIMAX(
        train_series,
        order=(1, 1, 1),
        seasonal_order=(1, 1, 1, 7),
    ).fit(disp=False)


def _fit_exponential_smoothing(train_series: pd.Series) -> Any:
    seasonal = "add" if len(train_series) >= 14 else None
    model = ExponentialSmoothing(
        train_series,
        trend="add",
        seasonal=seasonal,
        seasonal_periods=7 if seasonal else None,
        initialization_method="estimated",
    )
    return model.fit()


def _get_model_parameters(model_name: str, custom_parameters: Dict[str, Any]) -> Dict[str, Any]:
    return {"model": model_name, **custom_parameters}


def _persist_run_results(
    run_at: str,
    winner_model: str,
    winner_mae: float,
    currency_code: str,
    all_metrics: List[Dict[str, Any]],
    forecast_items: List[Dict[str, Any]],
) -> int:
    run_id = insert_training_run(
        run_at=run_at,
        method="auto_model_selection",
        winner_model=winner_model,
        winner_mae=winner_mae,
        currency_code=currency_code,
        notes="Antrenare automată ARIMA / SARIMAX / Exponential Smoothing",
    )
    for metrics in all_metrics:
        insert_model_result(
            run_id=run_id,
            model_name=metrics["model_name"],
            parameters_json=metrics["parameters_json"],
            mae=metrics["mae"],
            rmse=metrics["rmse"],
            mape=metrics["mape"],
        )
    for item in forecast_items:
        insert_forecast(
            run_id=run_id,
            model_name=winner_model,
            forecast_date=item["forecast_date"],
            predicted_value=item["predicted_value"],
            lower_bound=item["lower_bound"],
            upper_bound=item["upper_bound"],
            currency_code=currency_code,
        )
    return run_id


def train_models(
    data: Optional[pd.Series] = None,
    currency_code: str = "USD",
    forecast_horizon: int = 7,
) -> Dict[str, Any]:
    _ensure_models_directory()
    series = data if data is not None else _load_exchange_rate_series(currency_code)
    train_series, test_series = _train_test_split(series, test_size=14)

    candidates = [
        {
            "model_name": "ARIMA",
            "fit_fn": _fit_arima,
            "parameters": {"order": [2, 1, 2]},
        },
        {
            "model_name": "SARIMAX",
            "fit_fn": _fit_sarimax,
            "parameters": {"order": [1, 1, 1], "seasonal_order": [1, 1, 1, 7]},
        },
        {
            "model_name": "ETS",
            "fit_fn": _fit_exponential_smoothing,
            "parameters": {"trend": "add", "seasonal": "add" if len(train_series) >= 14 else None},
        },
    ]

    fit_results: List[Dict[str, Any]] = []
    for candidate in candidates:
        try:
            model = candidate["fit_fn"](train_series)
            metrics = evaluate_models(model=model, actual=test_series)
            fit_results.append(
                {
                    "model_name": candidate["model_name"],
                    "model": model,
                    "mae": metrics["mae"],
                    "rmse": metrics["rmse"],
                    "mape": metrics["mape"],
                    "parameters_json": json.dumps(
                        _get_model_parameters(candidate["model_name"], candidate["parameters"])
                    ),
                }
            )
        except Exception:
            continue

    if not fit_results:
        raise RuntimeError("Niciun model nu a putut fi antrenat cu datele disponibile.")

    best_result = min(fit_results, key=lambda candidate: (candidate["mae"], candidate["rmse"]))
    dump(best_result["model"], MODEL_FILENAME)

    forecast_info = generate_forecast(best_result["model"], forecast_horizon)
    forecast_dates = _build_forecast_dates(series.index.max(), forecast_horizon)
    forecast_items = [
        {
            "forecast_date": date,
            "predicted_value": float(entry["predicted"]),
            "lower_bound": float(entry["lower"]),
            "upper_bound": float(entry["upper"]),
        }
        for date, entry in zip(forecast_dates, forecast_info["forecast"])
    ]

    run_at = datetime.utcnow().isoformat()
    run_id = _persist_run_results(
        run_at=run_at,
        winner_model=best_result["model_name"],
        winner_mae=best_result["mae"],
        currency_code=currency_code,
        all_metrics=fit_results,
        forecast_items=forecast_items,
    )

    return {
        "success": True,
        "message": "Antrenare finalizată cu succes.",
        "run_id": run_id,
        "winner_model": best_result["model_name"],
        "winner_mae": best_result["mae"],
        "forecast_horizon": forecast_horizon,
        "forecast_records": len(forecast_items),
    }
