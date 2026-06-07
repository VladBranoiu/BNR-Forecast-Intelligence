def test_get_api_forecast_latest_returns_404_when_no_forecast(client):
    response = client.get("/api/forecast/latest")

    assert response.status_code == 404


def test_get_api_forecast_latest_returns_forecast(monkeypatch, client):
    def fake_fetch_latest_forecast(currency_code: str = "USD"):
        return {
            "run_id": 1,
            "winner_model": "SARIMAX",
            "winner_mae": 0.0321,
            "forecasts": [
                {
                    "forecast_date": "2026-06-08",
                    "predicted_value": 4.22,
                    "lower_bound": 4.1,
                    "upper_bound": 4.3,
                }
            ],
        }

    monkeypatch.setattr(
        "src.curs_bnr.backend.main.fetch_latest_forecast",
        fake_fetch_latest_forecast,
    )

    response = client.get("/api/forecast/latest")

    assert response.status_code == 200
    data = response.json()
    assert data["run_id"] == 1
    assert data["winner_model"] == "SARIMAX"
    assert data["winner_mae"] == 0.0321
    assert isinstance(data["forecasts"], list)
    assert len(data["forecasts"]) == 1
    assert data["forecasts"][0]["forecast_date"] == "2026-06-08"
    assert data["forecasts"][0]["predicted_value"] == 4.22
