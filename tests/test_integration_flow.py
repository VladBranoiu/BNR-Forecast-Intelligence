from datetime import datetime, timezone

from src.curs_bnr.backend.database import (
    insert_exchange_rate,
    insert_forecast,
    insert_training_run,
)


def test_integration_flow_succeeds_for_scrape_retrain_and_latest_forecast(monkeypatch, client):
    def fake_trigger_scraper(currency_code, start_date):
        insert_exchange_rate(currency_code, "2026-06-07", 4.5)
        return {
            "success": True,
            "currency_code": currency_code,
            "start_date": start_date,
            "records_count": 1,
            "message": "Datele BNR au fost salvate cu succes.",
        }

    monkeypatch.setattr(
        "src.curs_bnr.backend.main.trigger_scraper",
        fake_trigger_scraper,
    )

    scrape_response = client.post(
        "/api/scrape",
        json={"currency_code": "USD", "start_date": "24/02/2020"},
    )
    assert scrape_response.status_code == 200
    assert scrape_response.json()["success"] is True

    rates_response = client.get("/api/rates?currency_code=USD")
    assert rates_response.status_code == 200
    assert len(rates_response.json()) == 1

    mock_state = {}

    def fake_perform_retraining(currency_code, horizon):
        run_id = insert_training_run(
            run_at=datetime.now(timezone.utc).isoformat(),
            method="SARIMAX",
            winner_model="SARIMAX",
            winner_mae=0.1,
        )
        mock_state["run_id"] = run_id
        insert_forecast(
            run_id=run_id,
            model_name="SARIMAX",
            forecast_date="2026-06-08",
            predicted_value=4.55,
            lower_bound=4.45,
            upper_bound=4.65,
        )
        return {
            "success": True,
            "run_id": run_id,
            "winner_model": "SARIMAX",
            "winner_mae": 0.1,
            "forecast_horizon": horizon,
            "forecast_records": 1,
            "message": "Reantrenare mock finalizată.",
        }

    monkeypatch.setattr(
        "src.curs_bnr.backend.main.perform_retraining",
        fake_perform_retraining,
    )

    retrain_response = client.post(
        "/api/retrain",
        json={"currency_code": "USD", "forecast_horizon": 7},
    )
    assert retrain_response.status_code == 200
    assert retrain_response.json()["success"] is True

    forecast_response = client.get("/api/forecast/latest?currency_code=USD")
    assert forecast_response.status_code == 200
    data = forecast_response.json()
    assert data["run_id"] == mock_state["run_id"]
    assert data["winner_model"] == "SARIMAX"
    assert isinstance(data["forecasts"], list)
    assert data["forecasts"][0]["forecast_date"] == "2026-06-08"
    assert data["forecasts"][0]["predicted_value"] == 4.55
