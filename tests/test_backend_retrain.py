def test_post_api_retrain_delegates_to_service(monkeypatch, client):
    def fake_perform_retraining(currency_code, horizon):
        return {
            "success": True,
            "run_id": 1,
            "winner_model": "SARIMAX",
            "winner_mae": 0.12,
            "forecast_horizon": horizon,
            "forecast_records": horizon,
            "message": "Reantrenare mock finalizată.",
        }

    monkeypatch.setattr(
        "src.curs_bnr.backend.main.perform_retraining",
        fake_perform_retraining,
    )

    response = client.post(
        "/api/retrain",
        json={"currency_code": "USD", "forecast_horizon": 7},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["winner_model"] == "SARIMAX"
    assert data["forecast_horizon"] == 7


def test_post_api_retrain_returns_server_error_on_failure(monkeypatch, client):
    def fake_perform_retraining(currency_code, horizon):
        return {
            "success": False,
            "message": "Nu există suficiente date pentru reantrenare.",
        }

    monkeypatch.setattr(
        "src.curs_bnr.backend.main.perform_retraining",
        fake_perform_retraining,
    )

    response = client.post(
        "/api/retrain",
        json={"currency_code": "USD", "forecast_horizon": 7},
    )

    assert response.status_code == 500
    assert "Nu există suficiente date" in response.json()["detail"]
