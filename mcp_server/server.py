"""
server.py — Serveur MCP pour la vérification d'interactions médicamenteuses
=============================================================================
Expose un endpoint simple pour vérifier les interactions entre médicaments.
Sert aussi de démonstration de l'intégration MCP.
"""

import json
import os
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="MCP Server — Drug Interactions", version="1.0.0")

# Charger la base de données des interactions
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
INTERACTIONS_FILE = os.path.join(DATA_DIR, "medications.json")


def load_interactions() -> dict:
    """Charge les interactions médicamenteuses depuis le fichier JSON."""
    try:
        with open(INTERACTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"interactions": []}


class InteractionRequest(BaseModel):
    medications: list[str]


class InteractionResponse(BaseModel):
    result: str
    interactions_found: list[dict]


@app.get("/health")
def health():
    return {"status": "ok", "service": "mcp-drug-interactions"}


@app.post("/check_interactions", response_model=InteractionResponse)
def check_interactions(req: InteractionRequest):
    """Vérifie les interactions entre les médicaments fournis."""
    data = load_interactions()
    interactions_db = data.get("interactions", [])
    meds = [m.lower().strip() for m in req.medications]

    found = []
    for interaction in interactions_db:
        drugs = [d.lower() for d in interaction["drugs"]]
        # Vérifier si au moins 2 des médicaments fournis sont dans cette interaction
        matches = [m for m in meds if any(m in d or d in m for d in drugs)]
        if len(matches) >= 2:
            found.append({
                "drugs": interaction["drugs"],
                "severity": interaction["severity"],
                "description": interaction["description"],
            })

    if found:
        details = "\n".join(
            f"⚠️ {i['drugs'][0]} + {i['drugs'][1]} — "
            f"Sévérité: {i['severity']} — {i['description']}"
            for i in found
        )
        result = f"INTERACTIONS DÉTECTÉES ({len(found)}):\n{details}"
    else:
        result = "✅ Aucune interaction connue détectée entre ces médicaments."

    return InteractionResponse(result=result, interactions_found=found)


if __name__ == "__main__":
    import uvicorn
    print("🚀 Serveur MCP — Drug Interactions")
    print("   http://localhost:8001")
    print("   POST /check_interactions")
    uvicorn.run(app, host="0.0.0.0", port=8001)
