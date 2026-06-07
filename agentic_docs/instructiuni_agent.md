# Instrucțiuni agent

## Obiectiv
Agentul proiectului trebuie să ofere un chatbot integrat care răspunde la întrebări despre cursul valutar BNR, prognoze și starea aplicației. Chatbot-ul va avea acces la tool-uri locale pentru a extrage prognoza curentă, date recente și statistici de antrenare.

## Componente

- Model de conversație: un serviciu LLM care generează răspunsuri în limba română.
- Registru de tool-uri locale: funcții expuse de backend care permit accesul la date și prognoze.
- Interfață chat: componenta Streamlit care afișează dialogul și acceptă cereri.

## Funcționalități cheie

- Răspuns natural la întrebări despre evoluția cursului valutar.
- Apeluri automate către tool-urile backend pentru a obține:
  - ultima prognoză din baza de date;
  - cursurile BNR curente;
  - rezultatele ultimei rulări de antrenare.
- Gestionarea solicitărilor complexe de tip „compară modele”, „afișează graficul forecast” sau „actualizează datele”.

## Structura implementării

1. Definirea rolului chatbot-ului și a tipurilor de solicitări pe care le poate gestiona.
2. Crearea unui API local pentru tool-uri în backend.
3. Legarea frontend-ului Streamlit la API pentru a transmite cereri și a primi răspunsuri.
4. Definirea unui schelet inițial de tool calling, cu format JSON pentru apeluri de funcție.

## Observații

Aceste instrucțiuni sunt un ghid pentru dezvoltare. Nu se implementează încă logica completă a chatbot-ului, ci se păstrează o arhitectură clară pentru integrare ulterioară.
