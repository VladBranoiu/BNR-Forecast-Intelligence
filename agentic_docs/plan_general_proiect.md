# Plan general proiect

## Scop
Proiectul urmărește construirea unei aplicații pentru prognoza cursului valutar BNR, cu un backend FastAPI, un frontend Streamlit, scraping de date, bază de date SQLite, antrenare și reantrenare modele, vizualizări Plotly și chatbot cu tool-uri locale.

## Componente principale

- `scraper`: colectează date oficiale BNR și le pregătește pentru stocare.
- `backend`: expune API REST pentru date, prognoze, reantrenare și tool-uri chatbot.
- `frontend`: afișează tabel de cursuri, grafic forecast și un widget chatbot.
- `ml`: conține fluxul de antrenare și evaluare a modelelor.
- `chatbot`: gestionează interacțiunea utilizator-model și apelurile către tool-uri locale.

## Flux de dezvoltare

1. Definirea arhitecturii și a schemelor de date.
2. Crearea scraperului pentru datele BNR.
3. Stabilirea modelului de stocare SQLite.
4. Implementarea scheletului backend FastAPI.
5. Dezvoltarea frontend-ului Streamlit cu vizualizare și chat.
6. Definirea procesului de antrenare și evaluare modele.
7. Integrarea chatbot-ului cu tool-uri locale și ultima prognoză.

## Criterii de succes

- Aplicația rulează local la `http://localhost:7772` pentru backend.
- Frontend-ul afișează date și grafice relevante.
- Datele istorice BNR sunt colectate și stocate în SQLite.
- Există un mecanism de antrenare și reantrenare modele.
- Chatbot-ul poate apela tool-uri locale pentru informații actuale.
