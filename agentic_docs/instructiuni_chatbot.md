# Instrucțiuni chatbot

## Scop
Chatbot-ul va oferi răspunsuri în limba română pentru întrebări legate de cursul valutar BNR, prognoze și starea aplicației, folosind tool-uri locale definite în backend.

## Context
Aplicația include un backend FastAPI la `http://localhost:7772` și un frontend Streamlit. Chatbot-ul va comunica cu backend-ul pentru a obține date reale și a executa acțiuni specifice.

## Funcționalități principale

- Răspunsuri la întrebări despre cursul valutar curent și istoric.
- Afișarea ultimei prognoze disponibile.
- Solicitări pentru compararea modelelor și evaluarea performanței.
- Trimiterea de comenzi către backend pentru actualizarea datelor.

## Interacțiune cu tool-urile locale

- Chatbot-ul trebuie să distingă între întrebările care pot fi rezolvate prin text și cele care necesită apeluri de funcție.
- Pentru cererile de date actualizate sau prognoze, se va utiliza un format structurat de tool calling.
- Backend-ul trebuie să expună aceleași instrumente într-un registru clar, astfel încât chatbot-ul să le poată apela.

## Format de răspuns

- Răspuns natural: când utilizatorul solicită explicații, definiții sau comentarii.
- Tool call: când chatbot-ul decide să folosească un instrument local pentru date sau acțiuni.

## Observații

Aceste instrucțiuni sunt orientative pentru a păstra implementarea chatbot-ului modulară și pentru a facilita integrarea ulterioară cu backend-ul și frontend-ul.
