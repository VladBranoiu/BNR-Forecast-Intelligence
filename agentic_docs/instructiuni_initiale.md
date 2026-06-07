# Instrucțiuni inițiale

## Scopul principal
Acest proiect construiește o aplicație pentru prognoza cursului valutar BNR, utilizând un backend FastAPI la `http://localhost:7772`, un frontend Streamlit, un scraper dedicat, o bază de date SQLite, componente de antrenare modele și un chatbot integrat.

## Arhitectura aplicației

Aplicația este împărțită în module clare:
- `scraper`: colectează datele BNR și le inserează în baza SQLite.
- `backend`: expune API-ul REST, gestionează datele și probele de prognoză.
- `frontend`: afișează vizualizările și interfața de chat.
- `ml`: antrenează și reantrenează modele de prognoză.
- `chatbot`: conectează modelul de conversație la tool-urile locale.

## Condiții inițiale

- Nu se implementează încă logica completă, doar structura și documentația.
- Toate fișierele și planurile vor fi redactate în limba română.
- Directorul `agentic_docs` va conține planuri și instrucțiuni clare.

## Prima etapă

1. Crearea structurii de directoare și fișiere.
2. Documentarea componentelor de bază.
3. Stabilirea convențiilor pentru API, frontend și antrenare modele.
