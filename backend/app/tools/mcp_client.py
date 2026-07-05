"""
mcp_client.py — Client MCP pour vérification d'interactions médicamenteuses
=============================================================================
Se connecte au serveur MCP local pour vérifier les interactions entre médicaments.
"""

import httpx
from langchain_core.tools import tool


MCP_SERVER_URL = "http://localhost:8001"


@tool
def check_drug_interactions(medications: str) -> str:
    """Vérifie les interactions potentielles entre médicaments via le serveur MCP.

    Args:
        medications: Liste de médicaments séparés par des virgules.
    Returns:
        Résultat de la vérification des interactions.
    """
    try:
        response = httpx.post(
            f"{MCP_SERVER_URL}/check_interactions",
            json={"medications": [m.strip() for m in medications.split(",")]},
            timeout=10.0,
        )
        if response.status_code == 200:
            return response.json().get("result", "Aucune interaction trouvée.")
        return f"Erreur MCP (HTTP {response.status_code})"
    except httpx.ConnectError:
        return (
            "⚠️ Serveur MCP non disponible. "
            "Vérification des interactions non effectuée. "
            "Lancez le serveur MCP : cd mcp_server && python server.py"
        )
    except Exception as e:
        return f"Erreur lors de la vérification MCP : {str(e)}"
