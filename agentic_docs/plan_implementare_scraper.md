# Plan implementare scraper

## Obiectiv
Scraperul trebuie să colecteze date oficiale de curs valutar de la BNR și să le insereze într-o bază de date SQLite cu structură de tip serie temporală.

## Pași de implementare

1. Identificarea sursei de date BNR și a formatului de export.
2. Construirea unei componente care face HTTP request către sursă.
3. Parsarea datelor relevante (monedă, dată, curs) din răspuns.
4. Convertirea valorilor în format numeric și normalizarea datelor.
5. Salvarea în baza de date SQLite într-un tabel structurat.

## Structură recomandată

- `scraper/bnr_scraper.py` sau `scraper/main.py` cu funcții de preluare și parsare.
- `backend/services/data_service.py` pentru interacțiunea cu baza de date.
- Configurație în `src/curs_bnr/config.py` pentru URL-ul sursei.

## Validare

- Verificarea existenței coloanelor așteptate.
- Tratarea erorilor HTTP și a datelor lipsă.
- Testare cu un set mic de date pentru a confirma parsarea corectă.

## Observații

Scraperul va fi proiectat ca o componentă independentă care poate fi apelată din backend sau dintr-un script separat de inițializare.
