def test_post_api_scrape_delegates_to_service(monkeypatch, client):
    def fake_trigger_scraper(currency_code, start_date):
        return {
            "success": True,
            "currency_code": currency_code,
            "start_date": start_date,
            "records_count": 2,
            "message": "Simulare scrape BNR finalizată.",
        }

    monkeypatch.setattr(
        "src.curs_bnr.backend.main.trigger_scraper",
        fake_trigger_scraper,
    )

    response = client.post(
        "/api/scrape",
        json={"currency_code": "USD", "start_date": "24/02/2020"},
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["currency_code"] == "USD"
    assert response.json()["records_count"] == 2


def test_post_api_scrape_returns_server_error_on_failure(monkeypatch, client):
    def fake_trigger_scraper(currency_code, start_date):
        return {
            "success": False,
            "message": "Nu s-au putut obține datele din BNR.",
        }

    monkeypatch.setattr(
        "src.curs_bnr.backend.main.trigger_scraper",
        fake_trigger_scraper,
    )

    response = client.post(
        "/api/scrape",
        json={"currency_code": "USD", "start_date": "24/02/2020"},
    )

    assert response.status_code == 500
    assert "Nu s-au putut obține datele" in response.json()["detail"]
