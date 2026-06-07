# Plan implementare frontend

## Scop
Frontend-ul Streamlit va afișa datele valutar BNR, graficul cu forecastul celui mai bun model și un chatbot integrat.

## Componente principale

- Dashboard cu tabel și statistici de curs valutar.
- Vizualizare Plotly a evoluției și forecast-ului.
- Widget chat în front-end pentru interacțiunea utilizatorului.
- Zone pentru actualizare manuală a datelor și declanșare de reantrenare.

## Pagini și secțiuni propuse

- Pagina principală: prezentare generală, cursuri și stare model.
- Secțiunea forecast: grafic interactiv Plotly și detalii despre cea mai bună prognoză.
- Secțiunea chatbot: interfață de conversatie și butoane pentru tool-uri locale.

## Structură recomandată

- `frontend/app.py` - aplicația principală Streamlit.
- `frontend/ui_components.py` - componente vizuale reutilizabile.
- `frontend/chat_interface.py` - logica widget-ului chatbot.

## Observații

Frontend-ul trebuie să comunice cu backend-ul FastAPI și să ofere un flux clar pentru utilizatorii care verifică prognozele și dialogul.

---

## Selector Global de Monedă (Implementat)

### Scop
Permite utilizatorilor să selecteze moneda analizată (USD sau EUR) dintr-o singură locație (sidebar), iar această selecție să se propaghe automat pe toate taburile și apelurile API.

### Locație
- **Sidebar**: sub titlu, secțiunea "Monedă analizată"
- **Afișare card**: "Monedă curentă: {selectată}/RON"

### Implementare

#### 1. Session State
```python
if 'selected_currency' not in st.session_state:
    st.session_state['selected_currency'] = DEFAULT_CURRENCY  # USD implicit
```

#### 2. Selectbox în Sidebar
- Opțiuni: USD, EUR
- Sincronizare automată cu session_state
- Cheia session: `st.session_state['selected_currency']`

#### 3. Funcții care primesc moneda selectată

| Funcție | Parametru | Endpoint |
|---------|-----------|----------|
| `get_rates()` | `currency_code` | GET `/api/rates` |
| `trigger_scrape()` | `currency_code` | POST `/api/scrape` |
| `trigger_retrain()` | `currency_code` | POST `/api/retrain` |

#### 4. Taburi actualizate

- **Dashboard**: KPI curs → `{selected_currency}/RON`
- **Date & Scraping**: selectbox sincronizat, scraping pentru moneda selectată
- **Model & Reantrenare**: mesaj info, reantrenare pentru moneda selectată
- **Forecast**: grafice și KPI-uri dinamice după monedă
- **Chatbot**: indicator "Monedă implicită: {selected_currency}/RON"

### Cum funcționează

1. Utilizatorul selectează moneda din sidebar → session_state se actualizează
2. Toate componentele render_* citesc din session_state
3. Apelurile API trimit `currency_code=selected_currency` la backend
4. Datele afișate se schimbă instant pe toate taburile

### Teste manuale

```
1. Rulează: streamlit run src/curs_bnr/frontend/app.py
2. Selectează EUR din sidebar
3. Observă: Toate KPI-urile, tabelele și graficele arată date EUR/RON
4. Schimbă înapoi la USD → tot se actualizează
```

### Note
- ⚠️ TODO: Endpoint `/api/forecast/latest` — verifica dacă acceptă `currency_code`
- ✅ Session state persists pe toată sessiunea utilizatorului
- ✅ Design și styling nu sunt afectate (doar datele se schimbă)
