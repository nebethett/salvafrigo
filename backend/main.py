from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from backend.auth import authenticate_user, create_access_token, get_current_user
from pydantic import BaseModel, Field
from repository.ingredienti_repository import (
    get_categorie_con_ingredienti_db
)
import requests

app = FastAPI(title="Salvafrigo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3"  # oppure llama3, phi3, ecc.


class RicettaRequest(BaseModel):
    ingredienti: str = Field(..., min_length=1)
    tipo: str = Field(..., min_length=1)


class RicettaResponse(BaseModel):
    risposta: str

class Ingrediente(BaseModel):
    id: int
    nome: str = Field(..., min_length=1)
    quantita: int


class IngredientiResponse(BaseModel):
    ingredienti: list[Ingrediente]


class CategoriaConIngredienti(BaseModel):
    id: int
    nome: str = Field(..., min_length=1)
    ingredienti: list[Ingrediente]


class CategorieConIngredientiResponse(BaseModel):
    categorie: list[CategoriaConIngredienti]


@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username o password non validi",
        )

    token = create_access_token({"sub": user["username"]})

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@app.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user["username"]
    }


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


@app.post("/getCategorieConIngredienti", response_model=CategorieConIngredientiResponse)
def get_categorie_con_ingredienti():
    rows = get_categorie_con_ingredienti_db()

    categorie_dict = {}

    for row in rows:
        categoria_id = row["categoria_id"]

        if categoria_id not in categorie_dict:
            categorie_dict[categoria_id] = {
                "id": row["categoria_id"],
                "nome": row["categoria_nome"],
                "ingredienti": []
            }

        if row["ingrediente_id"] is not None:
            categorie_dict[categoria_id]["ingredienti"].append({
                "id": row["ingrediente_id"],
                "nome": row["ingrediente_nome"],
                "quantita": row["quantita_grammi"]
            })

    return CategorieConIngredientiResponse(
        categorie=[
            CategoriaConIngredienti(
                id=categoria["id"],
                nome=categoria["nome"],
                ingredienti=[
                    Ingrediente(
                        id=ingrediente["id"],
                        nome=ingrediente["nome"],
                        quantita=ingrediente["quantita"]
                    )
                    for ingrediente in categoria["ingredienti"]
                ]
            )
            for categoria in categorie_dict.values()
        ]
    )