# Plan implementare chatbot

## Obiectiv
Chatbot-ul va funcționa ca interfață naturală pentru utilizator, oferind informații despre cursurile BNR, prognoze și starea modelelor, folosind tool-uri locale atunci când este necesar.

## Componente

- Motor de conversație: un serviciu LLM integrat în backend sau apelat local.
- Tool registry: set de funcții în backend care pot fi apelate de chatbot.
- Frontend chat: componenta Streamlit care afișează dialogul și butoanele de interacțiune.

## Tipuri de solicitări

- Cerere directă privind cursul valutar curent.
- Cerere pentru ultima prognoză disponibilă.
- Cerere pentru comparații între modele.
- Cerere pentru actualizarea datelor sau rularea reantrenării.

## Flux de apeluri tool

1. Utilizatorul formulează o întrebare în chat.
2. Chatbot-ul analizează intenția.
3. Dacă este necesar, se apelează un tool local în backend.
4. Rezultatul este combinat cu un răspuns natural.

## Observații

În prima fază, chatbot-ul va avea funcționalitate de bază și va fi extins ulterior cu un registru clar de tool-uri locale.
