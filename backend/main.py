from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from backend.auth import authenticate_user, create_access_token, get_current_user
from pydantic import BaseModel, Field
from typing import List, Literal
from repository.ingredienti_repository import (
    get_categorie_con_ingredienti_db
)
import requests
import json

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
    ingredienti: str
    tipo: str

class RicettaPreview(BaseModel):
    id: int
    titolo: str
    sottotitolo: str
    prep_minuti: int
    cottura_minuti: int
    porzioni: int
    difficolta: Literal["Facile", "Media", "Difficile"]

class RicettaResponse(BaseModel):
    ricette: List[RicettaPreview]

class RicettaDettaglioRequest(BaseModel):
    titolo: str
    ingredienti: str
    tipo: str

class IngredienteRicetta(BaseModel):
    nome: str
    quantita: str

class RicettaDettaglioResponse(BaseModel):
    titolo: str
    sottotitolo: str
    prep_minuti: int
    cottura_minuti: int
    porzioni: int
    difficolta: Literal["Facile", "Media", "Difficile"]
    ingredienti: list[IngredienteRicetta]
    procedimento: list[str]
    consiglio_chef: str

class Ingrediente(BaseModel):
    id: int
    nome: str
    quantita: int


class IngredientiResponse(BaseModel):
    ingredienti: list[Ingrediente]

class CategoriaConIngredientiRequest(BaseModel):
    nome_ingrediente: str

class CategoriaConIngredienti(BaseModel):
    id: int
    nome: str
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
                "format": "json"
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

Strumento di cottura: {payload.tipo}

Rispondi SOLO con un oggetto JSON valido.
Non usare markdown.
Non usare ```json.
Non aggiungere commenti.
Non aggiungere testo fuori dal JSON.

Schema obbligatorio:
{{
  "ricette": [
    {{
      "id": 1,
      "titolo": "Nome ricetta",
      "sottotitolo": "Breve descrizione massimo 120 caratteri",
      "prep_minuti": 10,
      "cottura_minuti": 15,
      "porzioni": 2,
      "difficolta": "Facile"
    }}
  ]
}}

Regole:
- esattamente 3 ricette
- id deve essere 1, 2, 3
- prep_minuti deve essere SOLO un numero intero
- cottura_minuti deve essere SOLO un numero intero
- porzioni deve essere SOLO un numero intero
- difficolta solo: Facile, Media, Difficile
- prep_minuti + cottura_minuti massimo 30
- usa solo ingredienti indicati
"""
    risposta = chiama_ollama(prompt)
    try:
        data = json.loads(risposta)
        return RicettaResponse(**data)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=f"Ollama non ha restituito JSON valido: {risposta}"
        )

@app.post("/ricette/dettaglio", response_model=RicettaDettaglioResponse)
def genera_dettaglio_ricetta(payload: RicettaDettaglioRequest):
    prompt = f"""
Sei un generatore di JSON. Non devi mai usare markdown.

Crea il dettaglio completo della ricetta:
{payload.titolo}

Ingredienti disponibili:
{payload.ingredienti}

Strumento:
{payload.tipo}

Devi rispondere SOLO con un JSON valido.
NON scrivere ```json
NON scrivere testo prima o dopo
NON spiegare nulla

Formato obbligatorio:
{{
  "titolo": "string",
  "sottotitolo": "string",
  "prep_minuti": number,
  "cottura_minuti": number,
  "porzioni": number,
  "difficolta": "Facile | Media | Difficile",
  "ingredienti": [
    {{
      "nome": "string",
      "quantita": "string"
    }}
  ],
  "procedimento": [
    "string"
  ],
  "consiglio_chef": "string"
}}

Regole IMPORTANTI:
- usa SOLO gli ingredienti forniti
- prep_minuti deve essere SOLO un numero intero
- cottura_minuti deve essere SOLO un numero intero
- porzioni deve essere SOLO un numero intero
- massimo 7 step nel procedimento
- ogni step deve essere breve (1 frase)
- difficolta solo: Facile, Media, Difficile
- NON usare backtick
- NON usare markdown
- NON aggiungere testo fuori dal JSON

Rispondi ORA.
"""
    risposta = chiama_ollama(prompt)
    try:
        data = json.loads(risposta)
        return RicettaDettaglioResponse(**data)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=f"Ollama non ha restituito JSON valido: {risposta}"
        )


@app.post("/getCategorieConIngredienti", response_model=CategorieConIngredientiResponse)
def get_categorie_con_ingredienti(input : CategoriaConIngredientiRequest):
    rows = get_categorie_con_ingredienti_db(input.nome_ingrediente)

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