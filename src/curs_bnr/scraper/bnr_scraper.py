import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

DEFAULT_URL = "https://www.cursbnr.ro/curs-valutar-bnr"


def _normalize_number(value_text: str) -> float:
    """Normalizează un număr din format românesc către float Python."""
    text = value_text.strip().replace(" ", "")
    cleaned = re.sub(r"[^0-9,\.]+", "", text)
    if not cleaned:
        raise ValueError(f"Valoare numerică invalidă: '{value_text}'")
    if cleaned.count(",") > 0 and cleaned.count(".") > 0:
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    cleaned = cleaned.replace(",", ".")
    return float(cleaned)


def _normalize_date(date_text: str) -> str:
    """Transformă data în format ISO YYYY-MM-DD."""
    text = date_text.strip()
    for fmt in ("%d/%m/%Y", "%d.%m.%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(text, fmt)
            return parsed.date().isoformat()
        except ValueError:
            continue
    raise ValueError(f"Format de dată necunoscut: '{date_text}'")


def _find_rate_table(soup: BeautifulSoup) -> Optional[Tag]:
    table = soup.find("table", id="table-currencies")
    if table is not None:
        return table

    table = soup.find(
        "table",
        class_=["table", "table-md", "table-striped", "text-center"],
    )
    if table is not None:
        return table

    for candidate in soup.find_all("table"):
        rows = candidate.find_all("tr")
        if not rows:
            continue
        for row in rows:
            cells = [cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
            if len(cells) < 2:
                continue
            try:
                _normalize_date(cells[0])
            except ValueError:
                continue
            for cell in cells[1:]:
                try:
                    _normalize_number(cell)
                    return candidate
                except ValueError:
                    continue
    return None


def _find_numeric_value(cells: List[str]) -> float:
    """Găsește prima valoare numerică validă dintr-un rând."""
    for cell in cells:
        try:
            return _normalize_number(cell)
        except ValueError:
            continue
    raise ValueError("Nu s-a găsit nicio valoare numerică validă în rând.")


def parse_bnr_response(raw_html: str, currency_code: str) -> List[Dict[str, Any]]:
    """Parsează HTML-ul și extrage datele dintr-un tabel de cursuri BNR."""
    soup = BeautifulSoup(raw_html, "html.parser")
    table = _find_rate_table(soup)
    table_found = table is not None

    if not table_found:
        raise ValueError(
            "Tabelul de cursuri nu a fost găsit în răspunsul BNR."
        )

    rows = table.find_all("tr")
    results: List[Dict[str, Any]] = []

    for row in rows:
        if row.find("th") and not row.find_all("td"):
            continue

        cells = [cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
        if len(cells) < 2:
            continue

        try:
            rate_date = _normalize_date(cells[0])
            value = _find_numeric_value(cells[1:])
        except ValueError:
            continue

        results.append(
            {
                "currency_code": currency_code,
                "rate_date": rate_date,
                "value": value,
            }
        )

    if not results:
        snippet = raw_html[:500]
        error_message = (
            "Nu s-au găsit date valide în tabelul de cursuri. "
            "Verifică structura HTML și formatele de dată/număr."
        )
        logger.error(
            "Date trapezate eșuat: table_found=%s, row_count=%s, html_snippet=%s",
            table_found,
            len(rows),
            snippet,
        )
        raise ValueError(f"{error_message} Motiv: nu s-au extras rânduri valide.")

    logger.debug(
        "parse_bnr_response: table_found=%s row_count=%s valid_rows=%s",
        table_found,
        len(rows),
        len(results),
    )
    return results


def fetch_bnr_data(
    currency_code: str = "USD",
    start_date: str = "22/02/2020",
) -> List[Dict[str, Any]]:
    """Colectează datele BNR pentru un cod valutar și o dată de început."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    form_data = {
        "currency": currency_code,
        "dataStart": start_date,
        "butsub": "Afișează",
    }
    response = requests.post(
        DEFAULT_URL,
        data=form_data,
        headers=headers,
        timeout=20,
    )

    if response.status_code != 200:
        raise ConnectionError(
            "Pagina BNR nu a fost disponibilă "
            f"(status {response.status_code}). URL final: {response.url}."
        )

    try:
        return parse_bnr_response(response.text, currency_code)
    except Exception as exc:
        snippet = response.text[:500]
        logger.error(
            "Eroare la parsarea răspunsului BNR: status_code=%s url=%s table_found=%s row_count=%s html_snippet=%s",
            response.status_code,
            response.url,
            _find_rate_table(BeautifulSoup(response.text, "html.parser")) is not None,
            len(BeautifulSoup(response.text, "html.parser").find_all("tr")),
            snippet,
        )
        raise ValueError(
            "Nu s-au găsit date valide în tabelul de cursuri. "
            f"Motiv tehnic: {exc}. "
            f"URL final: {response.url}. "
            f"Fragment HTML: {snippet}"
        ) from exc
