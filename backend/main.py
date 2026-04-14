from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import requests

app = FastAPI(title="Salvafrigo API")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3"  # oppure llama3, phi3, ecc.


class RicettaRequest(BaseModel):
    ingredienti: str = Field(..., min_length=1)
    tipo: str = Field(..., min_length=1)


class RicettaResponse(BaseModel):
    risposta: str


def chiama_ollama(prompt: str) -> str:
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        return data["response"]
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Errore chiamata Ollama: {e}")
    except KeyError:
        raise HTTPException(status_code=500, detail="Risposta Ollama non valida")


@app.get("/")
def root():
    return {"message": "Salvafrigo API attiva"}


@app.post("/ricette", response_model=RicettaResponse)
def genera_ricette(payload: RicettaRequest):
    prompt = f"""
Genera ESATTAMENTE 3 ricette antispreco usando SOLO questi ingredienti:
{payload.ingredienti}

Vincoli:
- semplice
- economica
- pronta in meno di 30 minuti
- da preparare con questo strumento: {payload.tipo}

Rispondi SOLO nel seguente formato, senza aggiungere altro:
Titolo ricetta,1###Titolo ricetta,2###Titolo ricetta,3

Regole obbligatorie:
- scrivi ESATTAMENTE 3 ricette
- scrivi SOLO il titolo della ricetta
- NON scrivere descrizioni
- NON scrivere ingredienti
- NON scrivere preparazione
- dopo ogni titolo metti una virgola e un numero da 1 a 3 che rappresenta la difficoltà
- separa le 3 ricette solo con ###
- non andare a capo

Esempio di formato corretto:
Pasta al forno povera,2###Frittata di zucchine,1###Pollo al limone,3
"""
    risposta = chiama_ollama(prompt)
    return RicettaResponse(risposta=risposta)