# Plan implementare backend

## Scop
Backend-ul FastAPI trebuie să ofere endpoint-uri pentru datele BNR, prognoze, starea procesului de antrenare și instrumentele chatbot-ului.

## Endpoints propuse

- `GET /api/rates` - returnează lista de cursuri istorice și curente.
- `GET /api/forecast/latest` - returnează ultima prognoză disponibilă.
- `GET /api/runs?limit=1` - returnează informații despre ultima rulare de antrenare.
- `POST /api/scrape` - declanșează colectarea datelor BNR.
- `POST /api/retrain` - pornește un ciclu de reantrenare a modelelor.
- `POST /api/chat` - gestionează solicitările din chatbot și tool calling.

## Structură recomandată

- `backend/main.py` - inițializarea aplicației FastAPI.
- `backend/routes.py` - definiția endpoint-urilor.
- `backend/services/` - servicii pentru bază de date, scraping și modelare.
- `backend/schemas.py` - modele Pydantic pentru intrări și ieșiri.

## Conexiunea cu baza de date

- Utilizarea SQLAlchemy sau SQLModel pentru interacțiunea cu SQLite.
- Un serviciu dedicat pentru extragerea datelor de curs și a prognozelor.
- Gestionarea corectă a sesiunilor și a conexiunii în aplicație.

## Observații

Backend-ul trebuie să fie suficient de modular pentru a permite extinderea ulterioară cu noi instrumente și surse de date.
