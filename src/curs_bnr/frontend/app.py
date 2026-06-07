import json
from datetime import date, datetime
from typing import Any, Dict, List, Optional
import html

import plotly.graph_objects as go
import os
import requests
import streamlit as st
from dotenv import load_dotenv
from src.curs_bnr.chatbot import model_utils as chatbot_model_utils

# Încarcă variabilele de mediu din `.env` (dacă există)
load_dotenv()
load_dotenv('.env.example')

# URL backend (suprascris din env: BNR_BACKEND_URL)
BACKEND_URL = os.getenv('BNR_BACKEND_URL', 'http://localhost:7772')
DEFAULT_CURRENCY = 'USD'
DEFAULT_START_DATE = '22/02/2020'
# Timeout pentru cererile HTTP către backend (în secunde)
TIMEOUT_SECONDS = 45


def inject_custom_css() -> None:
    """Injectează stiluri CSS personalizate pentru o interfață modernă."""
    css = """
    <style>
    :root {
        --bg: linear-gradient(180deg, #071224 0%, #0c1b35 45%, #122946 100%);
        --card: rgba(9, 16, 34, 0.92);
        --card-border: rgba(34, 211, 238, 0.16);
        --accent: #22d3ee;
        --accent-soft: rgba(34, 211, 238, 0.14);
        --success: #2dd4bf;
        --danger: #f87171;
        --text: #eef5ff;
        --muted: #b0c8e8;
        --shadow: 0 24px 72px rgba(0, 0, 0, 0.28);
        font-family: 'Inter', system-ui, sans-serif;
    }

    .main > div.block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(12px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes softGlow {
        0%, 100% {
            box-shadow: 0 0 0 0 rgba(34, 211, 238, 0.18);
        }
        50% {
            box-shadow: 0 0 18px 0 rgba(34, 211, 238, 0.08);
        }
    }

    @keyframes dividerFlow {
        0% {
            background-position: 0% 50%;
        }
        100% {
            background-position: 100% 50%;
        }
    }

    .hero-card,
    .section-card,
    .kpi-card,
    .chat-card,
    .info-card {
        border-radius: 20px;
        background: var(--card);
        border: 1px solid var(--card-border);
        box-shadow: var(--shadow);
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        color: var(--text);
        backdrop-filter: blur(18px);
        animation: fadeInUp 0.45s ease both;
        transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
    }

    .hero-card {
        padding: 2rem;
        background: linear-gradient(135deg, rgba(8, 17, 34, 0.94), rgba(13, 31, 56, 0.94));
    }

    .hero-title {
        font-size: 2.8rem;
        line-height: 1.05;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }

    .hero-subtitle {
        color: #9fb9e6;
        font-size: 1.05rem;
        margin-bottom: 1rem;
    }

    .pulse-dot {
        display: inline-block;
        width: 0.65rem;
        height: 0.65rem;
        border-radius: 999px;
        margin-right: 0.55rem;
        background: #34d399;
        box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.32);
        animation: softGlow 1.8s ease-in-out infinite;
        vertical-align: middle;
    }

    .status-badge.success .pulse-dot {
        background: #34d399;
    }

    .status-badge.warning .pulse-dot {
        background: #38bdf8;
    }

    .status-badge.error .pulse-dot {
        background: #fb923c;
        animation: none;
    }

    .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        background: rgba(34, 211, 238, 0.14);
        color: #dbeafe;
        font-size: 0.82rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1rem;
    }

    .kpi-card h4 {
        margin: 0 0 0.4rem 0;
        color: var(--text);
        font-size: 1rem;
    }

    .kpi-card strong {
        font-size: 1.7rem;
        display: block;
        margin-bottom: 0.25rem;
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.45rem 0.8rem;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.75rem;
    }

    .status-badge.success { background: rgba(45, 212, 191, 0.18); color: #a7f3d0; }
    .status-badge.error { background: rgba(248, 113, 113, 0.18); color: #fecaca; }
    .status-badge.warning { background: rgba(34, 211, 238, 0.14); color: #bfdbfe; }

    .chat-info-card {
        background: rgba(6, 14, 34, 0.96);
        border: 1px solid rgba(34, 211, 238, 0.24);
        padding: 1.4rem 1.5rem;
        margin-bottom: 1.25rem;
    }

    .chat-info-card h4 {
        margin: 0 0 0.8rem 0;
        font-size: 1.15rem;
        color: var(--text);
    }

    .chat-info-list {
        margin: 0;
        padding-left: 1.25rem;
        color: #d3dce8;
        line-height: 1.7;
    }

    .chat-info-list li {
        margin-bottom: 0.55rem;
    }

    .chat-info-list li::marker {
        color: var(--accent);
    }

    .prompt-chip {
        display: inline-flex;
        align-items: center;
        padding: 0.45rem 0.85rem;
        border-radius: 999px;
        background: rgba(34, 211, 238, 0.12);
        color: var(--text);
        font-size: 0.88rem;
        margin-right: 0.55rem;
        margin-top: 0.5rem;
    }

    .chat-card {
        margin-top: 1rem;
        border-radius: 20px;
        background: rgba(10, 18, 34, 0.95);
        border-color: rgba(255, 255, 255, 0.08);
    }

    .chat-message {
        padding: 1rem 1.25rem;
        border-radius: 20px;
        margin-bottom: 0.75rem;
        line-height: 1.65;
        background: rgba(10, 20, 36, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.05);
        animation: fadeInUp 0.35s ease both;
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }

    .chat-message:hover {
        transform: translateY(-1px);
        box-shadow: 0 12px 28px rgba(34, 211, 238, 0.08);
    }

    .chat-user {
        background: rgba(46, 110, 255, 0.14);
        border-color: rgba(46, 110, 255, 0.22);
    }

    .chat-bot {
        background: rgba(34, 211, 238, 0.14);
        border-color: rgba(34, 211, 238, 0.22);
    }

    .section-card .section-title {
        margin-top: 0;
        margin-bottom: 0.95rem;
        color: var(--text);
        position: relative;
        padding-bottom: 0.55rem;
    }

    .section-card .section-title::after {
        content: '';
        position: absolute;
        left: 0;
        bottom: 0;
        width: 56px;
        height: 2px;
        border-radius: 999px;
        background: rgba(34, 211, 238, 0.24);
    }

    .info-card {
        border-left: 3px solid rgba(34, 211, 238, 0.5);
        padding: 1rem 1.2rem;
        background: rgba(7, 14, 29, 0.92);
        border-radius: 18px;
        animation: fadeInUp 0.45s ease both;
        transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
    }

    .hero-card:hover,
    .section-card:hover,
    .kpi-card:hover,
    .chat-card:hover,
    .info-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.45);
        box-shadow: 0 24px 70px rgba(14, 165, 233, 0.16);
    }

    .kpi-card strong {
        font-size: 1.7rem;
        display: block;
        margin-bottom: 0.25rem;
        text-shadow: 0 2px 18px rgba(56, 189, 248, 0.12);
    }

    .soft-divider {
        height: 1px;
        background: linear-gradient(90deg, rgba(34, 211, 238, 0.10), rgba(56, 189, 248, 0.24), rgba(34, 211, 238, 0.10));
        background-size: 200% 100%;
        margin: 0.8rem 0 1rem 0;
        border-radius: 999px;
        animation: dividerFlow 6s linear infinite;
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.55rem;
        padding: 0.45rem 0.8rem;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.75rem;
    }

    .status-badge.success {
        background: rgba(45, 212, 191, 0.18);
        color: #a7f3d0;
    }

    .status-badge.error {
        background: rgba(248, 113, 113, 0.18);
        color: #fecaca;
    }

    .status-badge.warning {
        background: rgba(34, 211, 238, 0.14);
        color: #bfdbfe;
    }

    .footer-note {
        color: var(--muted);
        font-size: 0.9rem;
        text-align: center;
        padding-top: 1rem;
        opacity: 0.9;
    }

    .streamlit-expanderHeader {
        color: #eef2ff;
    }

    div[data-testid="stWidgetLabel"] label {
        color: #e2eef6 !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }

    .section-card.compact-form {
        padding: 1.5rem !important;
        margin-bottom: 0.75rem !important;
        border-radius: 18px !important;
    }

    .scrape-button-spacer {
        height: 1.72rem;
    }

    .soft-divider {
        height: 1px;
        background: rgba(255, 255, 255, 0.08);
        margin: 0.8rem 0 1rem 0;
        border-radius: 999px;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea {
        background: rgba(10, 18, 34, 0.94) !important;
        color: var(--text) !important;
        border: 1px solid rgba(34, 211, 238, 0.18) !important;
        border-radius: 16px !important;
        min-height: 56px !important;
        padding: 0.95rem 1rem !important;
        box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.03);
        font-size: 1rem !important;
        transition: border-color 0.22s ease, box-shadow 0.22s ease;
    }

    div[data-testid="stTextArea"] textarea {
        min-height: 130px !important;
        resize: none !important;
    }

    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus,
    div[data-testid="stDateInput"] div[data-baseweb="input"] > div:focus-within,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {
        outline: none !important;
        border-color: rgba(34, 211, 238, 0.55) !important;
        box-shadow: 0 0 0 4px rgba(34, 211, 238, 0.12) !important;
    }

    div[data-testid="stDateInput"] div[data-baseweb="input"] > div,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background: rgba(10, 18, 34, 0.96) !important;
        color: var(--text) !important;
        border: 1px solid rgba(34, 211, 238, 0.22) !important;
        border-radius: 14px !important;
        display: flex !important;
        align-items: center !important;
        min-height: 58px !important;
        height: 58px !important;
        padding: 0 1rem !important;
        box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.03);
    }

    div[data-testid="stSelectbox"] div[data-baseweb="select"] input {
        opacity: 0 !important;
        width: 1px !important;
        height: 1px !important;
        padding: 0 !important;
        margin: 0 !important;
        pointer-events: none !important;
        position: absolute !important;
    }

    div[data-testid="stSelectbox"] div[data-baseweb="select"] [role="option"] {
        background: rgba(10, 18, 34, 0.98) !important;
        color: var(--text) !important;
        padding: 0.9rem 1rem !important;
        min-height: 48px !important;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    div[data-testid="stSelectbox"] div[data-baseweb="select"] span {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
    }

    div[data-testid="stSelectbox"] div[data-baseweb="select"] [role="option"]:hover {
        background: rgba(34, 211, 238, 0.1) !important;
    }

    div[data-testid="stSelectbox"] div[data-baseweb="select"] span {
        width: 100%;
        text-align: center;
        font-weight: 600;
    }

    div[data-testid="stSelectbox"] div[data-baseweb="select"] svg {
        color: var(--accent) !important;
        fill: var(--accent) !important;
    }

    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover {
        border-color: rgba(34, 211, 238, 0.35) !important;
        box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.08) !important;
    }

    div[data-testid="stFormSubmitButton"] {
        display: flex !important;
        align-items: center !important;
        height: 58px !important;
    }

    div[data-testid="stFormSubmitButton"] button {
        width: 100% !important;
        min-height: 58px !important;
        height: 58px !important;
        border-radius: 14px !important;
        margin-top: 0 !important;
        background: linear-gradient(135deg, rgba(34, 211, 238, 0.2), rgba(37, 99, 235, 0.85)) !important;
        border: 1px solid rgba(34, 211, 238, 0.32) !important;
        color: var(--text) !important;
        font-weight: 700 !important;
        font-size: 0.98rem !important;
        transition: all 0.18s ease-in-out !important;
        box-shadow: 0 10px 24px rgba(34, 211, 238, 0.08);
    }

    div[data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-1px);
        border-color: rgba(34, 211, 238, 0.55) !important;
        box-shadow: 0 14px 30px rgba(34, 211, 238, 0.12);
    }

    div[data-testid="stAlert"] {
        border-radius: 18px !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
    }

    .container {
        background: var(--bg);
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_kpi_card(title: str, value: str, subtitle: str = '', accent: str = '#22b8ff') -> None:
    """Afișează un card KPI stilizat."""
    st.markdown(
        f"""
        <div class='kpi-card' style='border-left: 4px solid {accent};'>
            <h4>{title}</h4>
            <strong>{value}</strong>
            <div style='color: #cbd5e1;'>{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_badge(text: str, success: bool = True) -> None:
    """Afișează un badge de status pentru backend sau moduri active."""
    status_class = 'success' if success else 'warning'
    st.markdown(
        f"""
        <span class='status-badge {status_class}'>
            <span class='pulse-dot'></span>
            {text}
        </span>
        """,
        unsafe_allow_html=True,
    )


def check_backend_status() -> Dict[str, Any]:
    """Verifică dacă backendul este disponibil."""
    try:
        response = requests.get(f'{BACKEND_URL}/', timeout=TIMEOUT_SECONDS)
        if response.status_code == 200:
            try:
                msg = response.json().get('message', 'Backend disponibil')
            except Exception:
                msg = 'Backend disponibil'
            return {'ok': True, 'message': msg}
        return {'ok': False, 'message': f'Backend răspunde cu {response.status_code}'}
    except requests.exceptions.RequestException as error:
        return {'ok': False, 'message': f'Backend indisponibil: {error}'}


def get_rates(currency_code: str) -> Dict[str, Any]:
    """Preia lista de cursuri valutare din backend."""
    try:
        response = requests.get(
            f'{BACKEND_URL}/api/rates',
            params={'currency_code': currency_code},
            timeout=TIMEOUT_SECONDS,
        )
        if response.status_code != 200:
            return {'ok': False, 'message': f'Eroare la preluarea datelor: {response.status_code}', 'data': []}
        data = response.json()
        if not isinstance(data, list):
            return {'ok': False, 'message': 'Răspuns invalid de la backend.', 'data': []}
        return {'ok': True, 'message': 'Date disponibile', 'data': data}
    except requests.exceptions.RequestException as error:
        return {'ok': False, 'message': f'Eroare de rețea: {error}', 'data': []}


def trigger_scrape(currency_code: str, start_date: str) -> Dict[str, Any]:
    """Declanșează actualizarea datelor BNR prin backend."""
    try:
        response = requests.post(
            f'{BACKEND_URL}/api/scrape',
            json={'currency_code': currency_code, 'start_date': start_date},
            timeout=TIMEOUT_SECONDS,
        )
        if response.status_code != 200:
            return {'ok': False, 'message': f'Eroare scraping: {response.status_code}', 'payload': response.text}
        result = response.json()
        return {'ok': result.get('success', False), 'message': result.get('message', 'Răspuns fără mesaj'), 'payload': result}
    except requests.exceptions.Timeout:
        return {
            'ok': False,
            'message': 'Backendul a răspuns prea greu la cererea de scraping. Verificați dacă serverul rulează și încercați din nou.',
            'payload': None,
        }
    except requests.exceptions.RequestException as error:
        return {'ok': False, 'message': f'Eroare de rețea la scraping: {error}', 'payload': None}


def get_latest_forecast(currency_code: str = DEFAULT_CURRENCY) -> Dict[str, Any]:
    """Preia ultima prognoză din backend pentru moneda selectată."""
    try:
        response = requests.get(
            f'{BACKEND_URL}/api/forecast/latest',
            params={'currency_code': currency_code},
            timeout=TIMEOUT_SECONDS,
        )
        if response.status_code == 404:
            return {'ok': False, 'message': f'Nu există prognoză disponibilă pentru {currency_code}.', 'data': None}
        if response.status_code != 200:
            return {'ok': False, 'message': f'Eroare la preluarea prognozei: {response.status_code}', 'data': None}
        return {'ok': True, 'message': 'Prognoză disponibilă', 'data': response.json()}
    except requests.exceptions.RequestException as error:
        return {'ok': False, 'message': f'Eroare de rețea la forecast: {error}', 'data': None}


def normalize_forecast_payload(data: Any) -> list[Dict[str, Any]]:
    """Normalizează payload-ul forecast pentru a lucra cu o listă de prognoze."""
    if not data:
        return []

    forecasts = data.get('forecasts')
    if forecasts is None:
        if isinstance(data, dict) and data.get('forecast_date') is not None:
            return [data]
        return []
    if isinstance(forecasts, dict):
        return [forecasts]
    return list(forecasts)


def format_float(value: Any, precision: int = 4) -> str:
    """Format numeric sigur pentru afișare cu un număr fix de zecimale."""
    if isinstance(value, (int, float)):
        return f"{value:.{precision}f}"
    return 'N/A'


def get_latest_run() -> Dict[str, Any]:
    """Preia ultima rulare de reantrenare din backend."""
    try:
        response = requests.get(f'{BACKEND_URL}/api/runs', params={'limit': 1}, timeout=TIMEOUT_SECONDS)
        if response.status_code != 200:
            return {'ok': False, 'message': f'Eroare la preluarea rulării: {response.status_code}', 'data': []}
        data = response.json()
        if not isinstance(data, list):
            return {'ok': False, 'message': 'Răspuns invalid de la backend.', 'data': []}
        return {'ok': True, 'message': 'Rulare disponibilă', 'data': data}
    except requests.exceptions.RequestException as error:
        return {'ok': False, 'message': f'Eroare de rețea la rulări: {error}', 'data': []}


def trigger_retrain(currency_code: str) -> Dict[str, Any]:
    """Pornește reantrenarea pe backend."""
    try:
        response = requests.post(
            f'{BACKEND_URL}/api/retrain',
            json={'currency_code': currency_code, 'forecast_horizon': 7},
            timeout=TIMEOUT_SECONDS,
        )
        if response.status_code != 200:
            return {'ok': False, 'message': f'Eroare reantrenare: {response.status_code}', 'payload': response.text}
        result = response.json()
        return {'ok': result.get('success', False), 'message': result.get('message', 'Răspuns fără mesaj'), 'payload': result}
    except requests.exceptions.RequestException as error:
        return {'ok': False, 'message': f'Eroare de rețea la reantrenare: {error}', 'payload': None}


def build_kpis(rates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Construiește KPI-uri simple din lista de cursuri."""
    if not rates:
        return {'count': 0, 'latest_date': 'N/A', 'latest_value': 'N/A'}

    latest = sorted(rates, key=lambda item: item.get('rate_date', ''))[-1]
    return {
        'count': len(rates),
        'latest_date': latest.get('rate_date', 'N/A'),
        'latest_value': latest.get('value', 'N/A'),
    }


def render_hero_section(forecast_result: Dict[str, Any], status: Dict[str, Any]) -> None:
    """Afișează un bloc HERO modern cu titlu, subtitlu și badge-uri."""
    with st.container():
        st.markdown(
            f"""
            <div class='hero-card'>
                <div style='display: flex; flex-wrap: wrap; justify-content: space-between; gap: 1rem;'>
                    <div style='max-width: 60%;'>
                        <div class='hero-title'>BNR Forecast Intelligence</div>
                        <div class='hero-subtitle'>Analiză, prognoză și asistent AI pentru cursul valutar</div>
                        <div>
                            <span class='badge-pill'>FastAPI</span>
                            <span class='badge-pill'>Streamlit</span>
                            <span class='badge-pill'>SQLite</span>
                            <span class='badge-pill'>ML</span>
                            <span class='badge-pill'>OpenRouter</span>
                        </div>
                    </div>
                    <div style='max-width: 35%;'>
                        <div class='kpi-card' style='border-left: 4px solid #38bdf8;'>
                            <h4>Ultima prognoză</h4>
                            <strong>{format_float(forecast_result['data']['predicted_value']) if forecast_result['ok'] and forecast_result['data'] else 'N/A'}</strong>
                            <div style='color: #cbd5e1;'>Prognoză pentru {forecast_result['data']['forecast_date'] if forecast_result['ok'] and forecast_result['data'] else '–'}</div>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_dashboard() -> None:
    """Afișează tab-ul Dashboard cu carduri KPI și informații de stare."""
    status = check_backend_status()
    selected_currency = st.session_state.get('selected_currency', DEFAULT_CURRENCY)
    forecast_result = get_latest_forecast(selected_currency)
    run_result = get_latest_run()
    rates_result = get_rates(selected_currency)

    hero_forecast = None
    if forecast_result['ok'] and isinstance(forecast_result['data'], dict):
        forecasts = normalize_forecast_payload(forecast_result['data'])
        if forecasts:
            last_forecast = forecasts[-1]
            hero_forecast = {
                'predicted_value': last_forecast.get('predicted_value'),
                'forecast_date': last_forecast.get('forecast_date'),
            }

    hero_info = {
        'ok': forecast_result['ok'],
        'data': hero_forecast,
    }

    render_hero_section(hero_info, status)

    if status['ok']:
        render_status_badge('Backend online și gata de rulare', True)
    else:
        render_status_badge('Backend indisponibil', False)
        st.warning('Conectează backendul la http://localhost:7772 pentru date actualizate.')

    kpis = build_kpis(rates_result.get('data', []))
    winner_model = 'N/A'
    mae_value = 'N/A'
    if run_result['ok'] and run_result['data']:
        run = run_result['data'][0]
        winner_model = run.get('winner_model', 'N/A')
        mae_value = f"{run.get('winner_mae', 'N/A'):.4f}" if run.get('winner_mae') is not None else 'N/A'

    st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
    selected_currency = st.session_state.get('selected_currency', DEFAULT_CURRENCY)
    render_kpi_card('Ultima valoare curs', str(kpis['latest_value']), f'{selected_currency} / RON', '#38bdf8')
    render_kpi_card('Ultima dată disponibilă', kpis['latest_date'], 'Actualizare bază date', '#22c55e')
    render_kpi_card('Model câștigător', winner_model, 'Rulare recentă', '#f59e0b')
    render_kpi_card('MAE', mae_value, 'Calitate prognoză', '#8b5cf6')
    render_kpi_card('Număr observații', str(kpis['count']), 'Date istorice', '#38bdf8')
    render_kpi_card('Backend status', status['message'] if status['ok'] else 'Offline', 'Conexiune API', '#22c55e' if status['ok'] else '#ef4444')
    st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="section-card">', unsafe_allow_html=True)

        if forecast_result['ok'] and isinstance(forecast_result['data'], dict):
            forecasts = normalize_forecast_payload(forecast_result['data'])
            if forecasts:
                last_forecast = forecasts[-1]
                st.markdown(
                    f"<p style='color: #cbd5e1;'>Ultima prognoză: {last_forecast.get('predicted_value', 'N/A'):.4f} RON pe {last_forecast.get('forecast_date', 'N/A')} (selectat: {st.session_state.get('selected_currency', DEFAULT_CURRENCY)}).</p>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<p style='color: #cbd5e1;'>{forecast_result['message']}</p>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                f"<p style='color: #cbd5e1;'>{forecast_result['message']}</p>",
                unsafe_allow_html=True,
            )

        if run_result['ok'] and run_result['data']:
            run = run_result['data'][0]
            st.markdown(
                f"<p style='color: #cbd5e1;'>Ultima rulare executată la {run.get('run_at', 'N/A')} cu modelul {run.get('winner_model', 'N/A')}.</p>",
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)


def render_data_and_scraping() -> None:
    """Afișează tab-ul Date & Scraping cu formular stilizat."""
    st.header('Date & Scraping')

    with st.container():
        st.markdown('<div class="section-card compact-form">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">Actualizare date BNR</h3>', unsafe_allow_html=True)
        st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)

        with st.form('scrape_form'):
            col1, col2, col3 = st.columns([1, 1, 0.75])

            with col1:
                current_index = 0 if st.session_state.get('selected_currency', DEFAULT_CURRENCY) == 'USD' else 1
                currency_code = st.selectbox(
                    'Valută',
                    ['USD', 'EUR'],
                    index=current_index,
                    key='scrape_currency_selectbox',
                )
                st.session_state['selected_currency'] = currency_code

            with col2:
                try:
                    default_date = datetime.strptime(DEFAULT_START_DATE, '%d/%m/%Y').date()
                except Exception:
                    default_date = date(2020, 2, 22)
                selected_start_date = st.date_input(
                    'Data start',
                    value=default_date,
                    format='DD/MM/YYYY',
                )

            with col3:
                st.markdown('<div class="scrape-button-spacer"></div>', unsafe_allow_html=True)
                scrape_button = st.form_submit_button(
                    'Actualizează datele BNR',
                    use_container_width=True,
                )

            st.markdown(
                '<div style="color: #cbd5e1; margin-top: 0.5rem;">Selectați valuta și data de început pentru actualizarea istoricului de curs BNR.</div>',
                unsafe_allow_html=True,
            )
            if scrape_button:
                try:
                    start_date = selected_start_date.strftime('%d/%m/%Y')
                except Exception:
                    start_date = DEFAULT_START_DATE
                with st.spinner('Se actualizează datele...'):
                    result = trigger_scrape(currency_code.strip().upper(), start_date)
                if result['ok']:
                    st.success(result['message'])
                    try:
                        st.toast('Scraping finalizat cu succes!')
                    except Exception:
                        pass
                else:
                    st.error(result['message'])

        st.markdown('</div>', unsafe_allow_html=True)

    selected_currency = st.session_state.get('selected_currency', DEFAULT_CURRENCY)
    rates_result = get_rates(selected_currency)
    if rates_result['ok']:
        if rates_result['data']:
            st.markdown('### Tabel cursuri recente')
            st.dataframe(rates_result['data'], use_container_width=True)
        else:
            st.info('Nu există date de afișat.')
    else:
        st.error(rates_result['message'])


def render_model_and_retrain() -> None:
    """Afișează tab-ul Model & Reantrenare cu carduri de rezultat."""
    st.header('Model & Reantrenare')

    with st.container():
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">Control reantrenare</h3>', unsafe_allow_html=True)

        selected_currency = st.session_state.get('selected_currency', DEFAULT_CURRENCY)
        st.info(f'Reantrenarea va utiliza moneda: **{selected_currency}/RON**')

        if st.button('Reantrenează modelele', key='retrain_button'):
            with st.spinner('Se reantrenează modelele...'):
                result = trigger_retrain(selected_currency)
            if result['ok']:
                st.success(result['message'])
                try:
                    st.toast('Reantrenare finalizată!')
                except Exception:
                    pass
            else:
                st.error(result['message'])

        st.markdown('</div>', unsafe_allow_html=True)

    run_result = get_latest_run()
    if run_result['ok'] and run_result['data']:
        run = run_result['data'][0]
        winner_model = run.get('winner_model', '')
        winner_mae = format_float(run.get('winner_mae'))
        winner_rmse_value = run.get('winner_rmse')
        winner_mape_value = run.get('winner_mape')

        if winner_rmse_value is None and winner_model and isinstance(run.get('results'), list):
            for result in run['results']:
                if result.get('model_name') == winner_model:
                    winner_rmse_value = result.get('rmse')
                    break

        if winner_mape_value is None and winner_model and isinstance(run.get('results'), list):
            for result in run['results']:
                if result.get('model_name') == winner_model:
                    winner_mape_value = result.get('mape')
                    break

        winner_rmse = format_float(winner_rmse_value)
        winner_mape = format_float(winner_mape_value)

        st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
        render_kpi_card('Ultima rulare', run.get('run_at', 'N/A'), 'Data rulării', '#38bdf8')
        render_kpi_card('Model câștigător', winner_model or 'N/A', 'Model selectat', '#22c55e')
        render_kpi_card('MAE', winner_mae, 'Acuratețe model', '#f59e0b')
        render_kpi_card('RMSE', winner_rmse, 'Răspândire eroare', '#8b5cf6')
        render_kpi_card('MAPE', winner_mape, 'Procent eroare', '#38bdf8')
        st.markdown('</div>', unsafe_allow_html=True)

        if isinstance(run.get('results'), list) and run['results']:
            sorted_results = sorted(run['results'], key=lambda result: result.get('mae', float('inf')))
            table_rows = [
                {
                    'Model': result.get('model_name', 'N/A'),
                    'MAE': format_float(result.get('mae')),
                    'RMSE': format_float(result.get('rmse')),
                    'MAPE': format_float(result.get('mape')),
                }
                for result in sorted_results
            ]
            st.markdown('### Modele evaluate')
            st.table(table_rows)
        else:
            st.info('Nu există rezultate de modele pentru ultima rulare.')

        st.markdown('### Despre metricile de performanță')
        st.markdown(
            '- MAE măsoară eroarea medie absolută între predicții și valoarea reală.\n'
            '- RMSE sensibilizează diferențele mari între predicții.\n'
            '- MAPE arată procentual cât deviază prognoza față de valoarea reală.',
        )
    else:
        st.info(run_result['message'])


def build_history_forecast_chart(
    forecasts: List[Dict[str, Any]],
    historical_rates: List[Dict[str, Any]],
    winner_model: str,
    currency: str = 'USD',
) -> go.Figure:
    """Construiește graficul principal cu istoricul și forecastul modelului câștigător pe moneda selectată."""
    dates = [forecast.get('forecast_date') for forecast in forecasts]
    predicted = [forecast.get('predicted_value') for forecast in forecasts]
    lower = [forecast.get('lower_bound') for forecast in forecasts]
    upper = [forecast.get('upper_bound') for forecast in forecasts]

    fig = go.Figure()
    if historical_rates:
        hist_dates = [item.get('rate_date') for item in historical_rates]
        hist_values = [item.get('value') for item in historical_rates]
        fig.add_trace(
            go.Scatter(
                x=hist_dates,
                y=hist_values,
                mode='lines+markers',
                line=dict(color='#8b5cf6', width=2),
                marker=dict(size=6, color='#8b5cf6', line=dict(color='#0f172a', width=1)),
                name='Istoric curs',
                hovertemplate='<b>%{x}</b><br>Istoric: %{y:.4f} RON',
            )
        )

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=predicted,
            mode='lines+markers',
            line=dict(color='#22d3ee', width=4),
            marker=dict(size=10, color='#22d3ee', line=dict(color='#0f172a', width=2)),
            name='Valoare prognozată',
            hovertemplate='<b>%{x}</b><br>Valoare prognozată: %{y:.4f} RON',
        )
    )

    if all(value is not None for value in lower + upper):
        fig.add_trace(
            go.Scatter(
                x=dates + dates[::-1],
                y=upper + lower[::-1],
                fill='toself',
                fillcolor='rgba(34, 211, 238, 0.16)',
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo='skip',
                name='Interval de încredere',
            )
        )

    if dates:
        fig.add_vline(
            x=dates[0],
            line=dict(color='#22d3ee', width=2, dash='dash'),
            annotation_text='Start forecast',
            annotation_position='top left',
            annotation_font=dict(color='#22d3ee', size=12),
        )

    fig.update_layout(
        title=f'Istoric și forecast curs {currency}/RON – model câștigător: {winner_model}',
        xaxis_title='Data',
        yaxis_title='Valoare (RON)',
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f8fafc'),
        hovermode='x unified',
        legend=dict(
            bgcolor='rgba(15, 23, 42, 0.85)',
            bordercolor='#22d3ee',
            borderwidth=1,
            orientation='h',
            yanchor='bottom',
            y=1.08,
            xanchor='right',
            x=1,
        ),
        xaxis=dict(
            type='date',
            tickformat='%d/%m/%Y',
            tickangle=-45,
            showgrid=True,
            gridcolor='rgba(255,255,255,0.08)',
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.08)',
            zeroline=False,
        ),
        margin=dict(t=80, b=60, l=60, r=40),
    )
    return fig


def build_forecast_zoom_chart(forecasts: List[Dict[str, Any]], currency: str = 'USD') -> go.Figure:
    """Construiește graficul de zoom pe prognoza modelului câștigător pentru moneda selectată."""
    dates = [forecast.get('forecast_date') for forecast in forecasts]
    predicted = [forecast.get('predicted_value') for forecast in forecasts]
    lower = [forecast.get('lower_bound') for forecast in forecasts]
    upper = [forecast.get('upper_bound') for forecast in forecasts]

    fig = go.Figure()
    marker_size = 16 if len(forecasts) == 1 else 10
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=predicted,
            mode='lines+markers',
            line=dict(color='#22d3ee', width=4),
            marker=dict(size=marker_size, color='#22d3ee', line=dict(color='#0f172a', width=2)),
            name='Valoare prognozată',
            hovertemplate='<b>%{x}</b><br>Valoare prognozată: %{y:.4f} RON',
        )
    )

    lower_exists = all(value is not None for value in lower)
    upper_exists = all(value is not None for value in upper)
    if lower_exists and upper_exists:
        fig.add_trace(
            go.Scatter(
                x=dates + dates[::-1],
                y=upper + lower[::-1],
                fill='toself',
                fillcolor='rgba(34, 211, 238, 0.16)',
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo='skip',
                name='Interval de încredere',
            )
        )

    value_candidates = [value for value in predicted if value is not None]
    if lower_exists:
        value_candidates.extend(lower)
    if upper_exists:
        value_candidates.extend(upper)

    if value_candidates:
        min_y = min(value_candidates)
        max_y = max(value_candidates)
        padding = max(0.01, (max_y - min_y) * 0.02)
        fig.update_yaxes(range=[min_y - padding, max_y + padding])

    fig.update_layout(
        title=f'Zoom pe prognoza modelului câștigător – {currency}/RON',
        xaxis_title='Data prognozei',
        yaxis_title='Valoare (RON)',
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f8fafc'),
        hovermode='x unified',
        legend=dict(
            bgcolor='rgba(15, 23, 42, 0.85)',
            bordercolor='#22d3ee',
            borderwidth=1,
            orientation='h',
            yanchor='bottom',
            y=1.08,
            xanchor='right',
            x=1,
        ),
        xaxis=dict(
            type='date',
            tickformat='%d/%m/%Y',
            tickangle=-45,
            showgrid=True,
            gridcolor='rgba(255,255,255,0.08)',
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.08)',
            zeroline=False,
        ),
        margin=dict(t=80, b=60, l=60, r=40),
    )
    return fig


def render_forecast() -> None:
    """Afișează tab-ul Forecast cu grafice detaliate și tabelul de prognoză."""
    st.header('Forecast')
    selected_currency = st.session_state.get('selected_currency', DEFAULT_CURRENCY)
    forecast_result = get_latest_forecast(selected_currency)
    if not forecast_result['ok']:
        st.info(forecast_result['message'])
        return

    forecast_data = forecast_result['data']
    if not isinstance(forecast_data, dict):
        st.info('Nu există prognoză disponibilă. Rulează mai întâi reantrenarea modelelor.')
        return

    forecasts = normalize_forecast_payload(forecast_data)
    if not forecasts:
        st.info('Nu există prognoză disponibilă. Rulează mai întâi reantrenarea modelelor.')
        return

    winner_model = forecast_data.get('winner_model', 'N/A')
    winner_mae_value = forecast_data.get('winner_mae')
    winner_mae = f"{winner_mae_value:.4f}" if isinstance(winner_mae_value, (int, float)) else 'N/A'
    forecast_count = len(forecasts)
    last_forecast_value = forecasts[-1].get('predicted_value')
    last_value = f"{last_forecast_value:.4f}" if isinstance(last_forecast_value, (int, float)) else 'N/A'

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h3 class="section-title">Forecast curs BNR</h3>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    selected_currency = st.session_state.get('selected_currency', DEFAULT_CURRENCY)

    st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
    render_kpi_card('Model câștigător', winner_model, 'Model selectat', '#22d3ee')
    render_kpi_card('MAE', winner_mae, 'Calitate prognoză', '#22d3ee')
    render_kpi_card('Zile prognozate', str(forecast_count), 'Număr zile', '#22d3ee')
    render_kpi_card('Ultima valoare prognozată', last_value, f'{selected_currency}/RON', '#22d3ee')
    st.markdown('</div>', unsafe_allow_html=True)

    rates_result = get_rates(selected_currency)
    historical_rates: List[Dict[str, Any]] = []
    if rates_result['ok'] and isinstance(rates_result['data'], list):
        sorted_rates = sorted(
            rates_result['data'],
            key=lambda item: item.get('rate_date', ''),
        )
        historical_rates = sorted_rates[-30:]

    history_forecast_chart = build_history_forecast_chart(forecasts, historical_rates, winner_model, selected_currency)
    st.plotly_chart(history_forecast_chart, use_container_width=True)

    zoom_forecast_chart = build_forecast_zoom_chart(forecasts, selected_currency)
    st.plotly_chart(zoom_forecast_chart, use_container_width=True)
    if forecast_count == 1:
        st.markdown(
            '<div class="info-card">Există o singură valoare de forecast disponibilă.</div>',
            unsafe_allow_html=True,
        )
    st.markdown(
        '<div class="info-card">Acest grafic detaliază doar perioada de forecast, pentru a evidenția variațiile pe termen scurt.</div>',
        unsafe_allow_html=True,
    )

    st.markdown('### Tabel prognoză')
    table_rows = []
    for forecast in forecasts:
        table_rows.append({
            'Data prognozei': forecast.get('forecast_date', 'N/A'),
            'Model': winner_model,
            'Valoare estimată': f"{forecast.get('predicted_value', 0):.4f}" if isinstance(forecast.get('predicted_value'), (int, float)) else 'N/A',
            'Limită inferioară': f"{forecast.get('lower_bound', 0):.4f}" if isinstance(forecast.get('lower_bound'), (int, float)) else 'N/A',
            'Limită superioară': f"{forecast.get('upper_bound', 0):.4f}" if isinstance(forecast.get('upper_bound'), (int, float)) else 'N/A',
        })

    st.table(table_rows)


def render_chatbot() -> None:
    """Afișează tab-ul Chatbot într-un container stilizat cu indicație de monedă selectată."""
    st.header('Chatbot')
    selected_currency = st.session_state.get('selected_currency', DEFAULT_CURRENCY)
    st.markdown(f'Întreabă asistentul despre curs, prognoză, modele sau actualizarea datelor. **Monedă implicită: {selected_currency}/RON**')

    st.markdown(
        """
        <div class='chat-info-card'>
            <h4>Cum funcționează chatbotul?</h4>
            <ul class='chat-info-list'>
                <li>Mod local fallback: folosește reguli simple și tool-uri locale pentru a interoga backendul aplicației.</li>
                <li>Poate răspunde despre cursuri, prognoze, modele, scraping și reantrenare.</li>
                <li>Dacă activezi LLM OpenRouter, întrebarea este interpretată de un model LLM, dar datele sunt tot preluate prin tool-urile aplicației.</li>
            </ul>
            <div style='margin-top: 0.8rem; color: #dbeafe; font-size: 0.95rem;'>Sugestie: activează LLM OpenRouter pentru întrebări mai flexibile și interpretări mai inteligente.</div>
            <div style='margin-top: 1rem; color: #dbeafe; font-size: 0.95rem;'>Exemple:</div>
            <div>
                <span class='prompt-chip'>Care este ultima prognoză?</span>
                <span class='prompt-chip'>Ce curs avem acum?</span>
                <span class='prompt-chip'>Compară modelele antrenate.</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    use_llm = st.checkbox('Folosește LLM prin OpenRouter dacă este disponibil', value=False)
    provider = chatbot_model_utils.get_llm_provider()
    llm_provider = 'OpenRouter' if provider in ('openrouter', 'openai') else 'Gemini' if provider == 'gemini' else None
    mode_text = 'Mod LLM OpenRouter activ' if use_llm and llm_provider else 'Mod local fallback'
    render_status_badge(mode_text, success=bool(use_llm and llm_provider))

    with st.form('chat_form', clear_on_submit=True):
        user_input = st.text_area('Mesaj către chatbot', '', height=140)
        send = st.form_submit_button('Trimite')

    if send and user_input:
        st.session_state['chat_history'].append(('user', user_input))
        with st.spinner('Chatbot procesează întrebarea...'):
            reply = chatbot_model_utils.run_chatbot(user_input, use_llm=use_llm)
        st.session_state['chat_history'].append(('bot', reply))

    for role, text in st.session_state.get('chat_history', []):
        css_class = 'chat-user' if role == 'user' else 'chat-bot'
        prefix = 'Tu' if role == 'user' else 'Asistent'
        safe_text = html.escape(text).replace('\n', '<br>')
        st.markdown(
            f"""
            <div class='chat-card'>
                <div class='chat-message {css_class}'>
                    <strong>{prefix}</strong><br>{safe_text}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_sidebar() -> None:
    """Configurează bara laterală cu informații despre proiect și selecter global de monedă."""
    st.sidebar.markdown('## BNR Forecast Intelligence')
    st.sidebar.markdown('**Dashboard financiar modern**')
    st.sidebar.markdown('---')
    
    st.sidebar.markdown('### Monedă analizată')
    selected_currency = st.sidebar.selectbox(
        'Selectați moneda',
        options=['USD', 'EUR'],
        index=0 if st.session_state.get('selected_currency', DEFAULT_CURRENCY) == 'USD' else 1,
        key='currency_selector',
    )
    st.session_state['selected_currency'] = selected_currency
    currency_pair = f'{selected_currency}/RON'
    st.sidebar.markdown(f"<div class='kpi-card'><strong>Monedă curentă: {currency_pair}</strong></div>", unsafe_allow_html=True)
    st.sidebar.markdown('---')
    
    st.sidebar.markdown('**Cum funcționează**')
    st.sidebar.markdown('- Conectare la backend FastAPI')
    st.sidebar.markdown('- Scraping BNR și stocare SQLite')
    st.sidebar.markdown('- Evaluare modele ML și prognoză')
    st.sidebar.markdown('- Chatbot local + LLM OpenRouter')
    st.sidebar.markdown('---')
    st.sidebar.markdown('**Notă**: nu sunt afișate chei sau date sensibile.')


def main() -> None:
    """Punctul de intrare pentru aplicația Streamlit."""
    st.set_page_config(
        page_title='BNR Forecast Intelligence',
        page_icon='📈',
        layout='wide',
    )

    if 'selected_currency' not in st.session_state:
        st.session_state['selected_currency'] = DEFAULT_CURRENCY

    inject_custom_css()
    render_sidebar()

    tabs = st.tabs([
        'Dashboard',
        'Date & Scraping',
        'Model & Reantrenare',
        'Forecast',
        'Chatbot',
    ])

    with tabs[0]:
        render_dashboard()
    with tabs[1]:
        render_data_and_scraping()
    with tabs[2]:
        render_model_and_retrain()
    with tabs[3]:
        render_forecast()
    with tabs[4]:
        render_chatbot()

    st.markdown('<hr style="border:none; height:1px; background: rgba(255, 255, 255, 0.08); margin: 1.5rem 0;">', unsafe_allow_html=True)
    st.markdown(
        '<div class="footer-note">Proiect final AIE – Prognoza cursului valutar BNR · FastAPI · Streamlit · SQLite · Plotly · OpenRouter</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
