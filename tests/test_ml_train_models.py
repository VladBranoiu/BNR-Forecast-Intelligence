import pandas as pd

from src.curs_bnr.ml.train_models import _load_exchange_rate_series


def test_load_exchange_rate_series_parses_iso_and_dayfirst_dates(monkeypatch):
    sample_rates = [
        {
            "id": 1,
            "currency_code": "USD",
            "rate_date": "2026-06-07",
            "value": 4.5,
            "created_at": "2026-06-07T14:00:25.317462",
        },
        {
            "id": 2,
            "currency_code": "USD",
            "rate_date": "07/12/2026",
            "value": 4.4,
            "created_at": "2026-12-07T14:00:25.317462",
        },
        {
            "id": 3,
            "currency_code": "EUR",
            "rate_date": "2026-06-07",
            "value": 1.0,
            "created_at": "2026-06-07T14:00:25.317462",
        },
    ]

    monkeypatch.setattr(
        "src.curs_bnr.ml.train_models.read_exchange_rates",
        lambda: sample_rates,
    )

    series = _load_exchange_rate_series("USD")

    assert len(series) == 2
    assert series.index.max() == pd.Timestamp("2026-12-07")
    assert series.index.min() == pd.Timestamp("2026-06-07")
    assert series.iloc[0] == 4.5
    assert series.iloc[-1] == 4.4
