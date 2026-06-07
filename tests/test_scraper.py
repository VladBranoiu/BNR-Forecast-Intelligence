import pytest

from src.curs_bnr.scraper.bnr_scraper import (
    _normalize_date,
    _normalize_number,
    parse_bnr_response,
)


def test_normalize_number_converts_comma_decimal():
    """Verifică conversia numărului cu virgulă zecimală în float."""
    assert _normalize_number("4,4395") == 4.4395
    assert _normalize_number("1.234,56") == 1234.56


@pytest.mark.parametrize(
    "value, expected",
    [
        ("24/02/2020", "2020-02-24"),
        ("24.02.2020", "2020-02-24"),
        ("24-02-2020", "2020-02-24"),
        ("2020-02-24", "2020-02-24"),
    ],
)
def test_normalize_date_formats(value, expected):
    """Verifică normalizarea datelor în format ISO."""
    assert _normalize_date(value) == expected


def test_parse_bnr_response_valid_html_with_table_currencies():
    """Verifică parsarea HTML-ului mock care conține tabelul de cursuri."""
    html = """
    <table id="table-currencies">
        <tr><th>Data</th><th>Valoare USD</th></tr>
        <tr><td>24.02.2020</td><td>4,4395</td></tr>
        <tr><td>25.02.2020</td><td>4,4355</td></tr>
    </table>
    """
    result = parse_bnr_response(html, "USD")

    assert len(result) == 2
    assert result[0]["rate_date"] == "2020-02-24"
    assert result[0]["value"] == 4.4395
    assert result[1]["rate_date"] == "2020-02-25"


def test_parse_bnr_response_missing_table_raises_value_error():
    """Verifică că lipsa tabelului conduce la eroare clară."""
    html = "<html><body><p>Fără tabel</p></body></html>"

    with pytest.raises(ValueError, match="Tabelul de cursuri"):
        parse_bnr_response(html, "USD")


def test_parse_bnr_response_ignores_invalid_rows():
    """Verifică că rândurile invalide sunt ignorate în parsare."""
    html = """
    <table id="table-currencies">
        <tr><th>Data</th><th>Valoare USD</th></tr>
        <tr><td>data invalidă</td><td>not-a-number</td></tr>
        <tr><td>26.02.2020</td><td>4,4280</td></tr>
    </table>
    """
    result = parse_bnr_response(html, "USD")

    assert len(result) == 1
    assert result[0]["rate_date"] == "2020-02-26"
    assert result[0]["value"] == 4.428
