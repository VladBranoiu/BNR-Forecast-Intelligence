# Instrucțiuni pentru antrenarea modelelor

## Obiectiv
Construirea unui flux de antrenare pentru modele de prognoză a cursului valutar BNR, cu posibilitate de reantrenare pe date actualizate.

## Date de intrare

- Date istorice de curs BNR stocate în SQLite.
- Serii temporale structurale cu dată, monedă și valoare curs.

## Direcții de modelare

- Definirea unei componente de preprocesare care curăță și pregătește seriile temporale.
- Identificarea caracteristicilor temporale relevante:
  - lag-uri,
  - ferestre de scor,
  - indicatori de trend și sezonalitate.
- Selectarea modelelor de testat și comparat.

## Metrici

- MAE (eroare absolută medie)
- RMSE (rădăcina medie a pătratului erorii)
- stabilitatea predicțiilor pe intervale de timp consecutive

## Scenariu de reantrenare

- Datele noi sunt adăugate în SQLite de scraper.
- Reantrenarea se pornește din backend și produce un model actualizat salvat în `models/`.
- Ultima versiune a modelului devine sursa pentru forecast-ul din frontend.

## Observații

Aceste instrucțiuni definesc un cadru pentru proiectarea pipeline-ului ML. Implementarea concretă va fi realizată ulterior, în etape clar separate.
