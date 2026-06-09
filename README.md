#  Prognoza cursului valutar BNR

Acest proiect este un prototip pentru o aplicație de prognoză a cursului valutar BNR, cu arhitectură backend FastAPI, frontend Streamlit și componente de scraping, stocare SQLite, antrenare modele și chatbot integrat.

## Componente principale

- `src/curs_bnr/backend`: API FastAPI care expune datele, prognozele și instrumentele locale.
- `src/curs_bnr/frontend`: interfață Streamlit pentru vizualizare, chat și explorare a prognozelor.
- `src/curs_bnr/scraper`: colectare de date BNR și procesare inițială.
- `src/curs_bnr/ml`: componente pentru antrenarea și reantrenarea modelelor de prognoză.
- `src/curs_bnr/chatbot`: integrarea chatbot-ului cu tool-uri locale și apeluri către backend.
- `data/`: datele istorice și fișierele de stare generate în timp.
- `models/`: modelele salvate și artefactele de predicție.
- `agentic_docs/`: planuri, instrucțiuni și concepte pentru dezvoltarea proiectului.

## Structură recomandată

```
proiect_final_AIE/
├── agentic_docs/
├── data/
├── models/
├── notebooks/
├── src/
│   └── curs_bnr/
│       ├── backend/
│       │   └── services/
│       ├── frontend/
│       ├── scraper/
│       ├── ml/
│       ├── chatbot/
│       └── config.py
├── tests/
├── requirements.txt
├── README.md
├── agentic_docs/pasi_rulare_proiect.md
├── .env.example
└── .gitignore
```

## Observații

Aceasta este o structură inițială. Implementarea logicii va respecta separarea clară între backend, frontend, scraper, ML și chatbot.

## Fișiere schelet create

- `src/curs_bnr/backend/main.py`
- `src/curs_bnr/backend/database.py`
- `src/curs_bnr/backend/schemas.py`
- `src/curs_bnr/backend/services/`
- `src/curs_bnr/frontend/app.py`
- `src/curs_bnr/scraper/bnr_scraper.py`
- `src/curs_bnr/ml/train_models.py`
- `src/curs_bnr/ml/evaluate_models.py`
- `src/curs_bnr/ml/forecast.py`
- `src/curs_bnr/ml/retrain.py`
- `src/curs_bnr/chatbot/tools.py`
- `src/curs_bnr/chatbot/tool_registry.py`
- `src/curs_bnr/chatbot/model_utils.py`
