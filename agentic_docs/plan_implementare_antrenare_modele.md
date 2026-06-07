# Plan implementare antrenare modele

## Obiectiv
Dezvoltarea unui flux de antrenare și reantrenare pentru modelele de prognoză ale cursului valutar BNR.

## Metodologie

1. Pregătirea datelor istorice din baza de date SQLite.
2. Transformarea seriilor temporale pentru modelare.
3. Selectarea modelelor candidate:
   - modele autoregresive (ARIMA/SARIMAX),
   - modele de regresie bazate pe ferestre de timp,
   - modele de tip ensemble sau regresie liniară avansată.
4. Evaluarea performanței cu metrici precum MAE și RMSE.
5. Salvarea celui mai bun model în directorul `models/`.

## Reantrenare

- Reantrenarea se va efectua pe baza datelor actualizate.
- În mod ideal, aplicația trebuie să poată declanșa un proces de reantrenare din backend.
- Modelele antrenate vor fi versiuni etichetate și vor putea fi comparate.

## Structură recomandată

- `ml/data_preparation.py` pentru transformări și curățare.
- `ml/train.py` pentru logica de antrenare și evaluare.
- `ml/evaluate.py` pentru metrice și raportare.

## Observații

Acest plan se concentrează pe arhitectura de antrenare, nu pe implementarea concretă a fiecărui model în prima etapă.
