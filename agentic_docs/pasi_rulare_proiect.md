# Pași rulare proiect

## 1. Configurare inițială

1. Clonare repository în directorul local.
2. Creare mediu virtual Python.
3. Instalare dependențe:
   ```bash
   pip install -r requirements.txt
   ```
4. Copiere fișier `.env.example` în `.env` și adaptare după necesități.

## 2. Pregătire date

- Verifică existența directorului `data/`.
- Rulează scraperul pentru a popula baza de date cu date BNR noi.
- Confirmă starea datelor în baza SQLite.

## 3. Pornire backend

- Rulează backend-ul FastAPI:
  ```bash
  uvicorn src.curs_bnr.backend.main:app --host 127.0.0.1 --port 7772 --reload
  ```
- Verifică endpoint-urile de bază.

## 4. Pornire frontend

- Rulează frontend-ul Streamlit:
  ```bash
  streamlit run src/curs_bnr/frontend/app.py
  ```
- Deschide interfața în browser la `http://localhost:8501`.

## 5. Testare funcțională

- Testează afișarea cursurilor și a graficelor.
- Verifică integritatea datelor în SQLite.
- Testează chat-ul și apelurile către tool-urile backend.

### Selector global de monedă

După pornirea frontend-ului, observă **sidebar-ul din stânga**:
- Secțiunea "Monedă analizată" conține un selectbox
- Selectează **USD** sau **EUR**
- **Toate datele se actualizează instantaneu** pe toate taburile:
  - Dashboard: KPI curs arată moneda selectată
  - Date & Scraping: tabel și scraping pentru moneda aleasă
  - Model & Reantrenare: reantrenare pentru moneda aleasă
  - Forecast: grafice și prognoza pentru moneda selectată
  - Chatbot: indicator "Monedă implicită: {selectată}/RON"

**Exemplu**: 
1. Selectează EUR din sidebar
2. Mergi la tab "Dashboard" → vei vedea `EUR/RON`
3. Mergi la tab "Forecast" → grafice și prognoza vor fi pe EUR
4. Initiate scraping din "Date & Scraping" → va prelua date EUR

## 6. Extindere ulterioară

- Adaugă teste automate în `tests/`.
- Completează documentația din `agentic_docs/` pe măsură ce dezvoltarea avansează.
