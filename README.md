# salvafrigo
App per creazione ricette salvafrigo e antispreco

# RUN STREAMLIT
ollama serve
python -m fastapi dev backend/main.py
python -m streamlit run frontend/app.py
pip install -r requirements.txt *per installare tutto il necessario*

# REGOLE BASE
- Scrivi un prompt più preciso che puoi e cosa ti aspetti realmente in output
- usa sempre .strip() per evitare spazi o formati strani nelle risposte del modello

# FAST API
Far parlare il frontend con una API FastAPI per gestire input, validare i dati e poi chiamare ollama.
- tieni separata la logica AI dalla UI
- domani puoi cambiare Streamlit senza toccare il backend
- puoi riusare la stessa API anche da app mobile o frontend web
- FastAPI ti valida gli input con modelli Pydantic e ti documenta automaticamente gli endpoint.
