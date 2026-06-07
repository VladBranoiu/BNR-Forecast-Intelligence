# Concept tool calling

## Definiție
Tool calling se referă la mecanismul prin care chatbot-ul sau modelul de conversație apelează funcții locale definite în aplicație pentru a obține date concrete sau a executa acțiuni.

## Scop
Principalul beneficiu este separarea între generarea limbajului natural și executarea logicii aplicației. Astfel, chatbot-ul poate rămâne un director de dialog, iar datele reale sunt furnizate de tool-urile backend.

## Exemple de tool-uri locale

- `get_latest_forecast()` - obține ultima prognoză din baza de date.
- `get_current_rates()` - returnează cursurile BNR recente.
- `trigger_scraper()` - pornește scrapingul de date BNR.
- `trigger_retrain()` - lansează procesul de reantrenare.

## Format de interacțiune

Tool calling poate fi reprezentat printr-un obiect JSON care conține:
- numele funcției,
- parametrii necesari,
- contextul conversației.

## Avantaje

- Crește transparența și controlul asupra acțiunilor chatbot-ului.
- Permite aplicației să păstreze datele actuale în backend, fără a le improviza.
- Facilitează testarea și extinderea cu noi funcționalități.

## Observații

În această etapă, se pregătește arhitectura conceptului. Implementarea concretă va respecta separarea între dialog și execuția funcțiilor.
