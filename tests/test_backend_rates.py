from src.curs_bnr.backend import database as db


def test_get_api_rates_returns_empty_list_when_no_data(client):
    """Verifică că GET /api/rates returnează o listă goală dacă nu există date."""
    response = client.get("/api/rates?currency_code=USD")

    assert response.status_code == 200
    assert response.json() == []


def test_get_api_rates_filters_by_currency(client):
    """Verifică că filtrarea după currency_code funcționează."""
    db.insert_exchange_rate("USD", "2026-06-07", 4.5)
    db.insert_exchange_rate("EUR", "2026-06-07", 5.0)

    response = client.get("/api/rates?currency_code=EUR")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["currency_code"] == "EUR"
    assert data[0]["value"] == 5.0
