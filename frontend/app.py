import streamlit as st
import requests

st.set_page_config(page_title="Salvafrigo AI", page_icon="🍳")

st.title("🍳 Salvafrigo AI")

ingredienti = st.text_input("Inserisci ingredienti:")
tipo = st.selectbox(
    "Scegli come cucinare",
    ["Bimby", "Friggitrice ad aria", "Padella"]
)

def mostra_card(titolo: str, difficolta: str) -> None:
    with st.container(border=True):
        st.subheader(titolo)
        st.write(f"Difficoltà: {difficolta}")

if st.button("Trova ricetta"):
    if ingredienti.strip():
        try:
            response = requests.post(
                "http://127.0.0.1:8000/ricette",
                json={
                    "ingredienti": ingredienti,
                    "tipo": tipo
                },
                timeout=120
            )
            response.raise_for_status()
            data = response.json()

            elementi = [e.strip() for e in data["risposta"].split("###") if e.strip()]

            for ricetta in elementi:
                try:
                    titolo, difficolta = ricetta.rsplit(",", 1)
                    difficolta_num = int(difficolta.strip())
                    stelle = "⭐" * max(1, min(difficolta_num, 3))
                    mostra_card(f"🍽️ {titolo.strip()}", stelle)
                except Exception:
                    mostra_card(f"🍽️ {ricetta}", "⭐")
        except requests.RequestException as e:
            st.error(f"Errore chiamando il backend: {e}")
    else:
        st.warning("Devi inserire gli ingredienti!")