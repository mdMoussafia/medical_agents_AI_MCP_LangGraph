"""
physician_review.py — Revue du Médecin Traitant (Human-in-the-Loop)
=====================================================================
Ce nœud interrompt le workflow pour permettre au médecin
de valider la synthèse et proposer un traitement.
"""

from langchain_core.messages import AIMessage


def physician_review_node(state: dict) -> dict:
    """
    Human-in-the-Loop : le médecin reçoit la synthèse clinique
    et la recommandation, puis propose un traitement.

    Si le traitement n'est pas encore fourni, on marque l'état
    comme 'awaiting_input: physician' pour que l'API interrompe
    le workflow et attende l'input du médecin.
    """
    physician_treatment = state.get("physician_treatment", "")

    if physician_treatment:
        # Le médecin a déjà répondu → continuer
        print("   👨‍⚕️ Traitement du médecin reçu")
        return {
            "awaiting_input": "",
            "messages": [
                AIMessage(
                    content=f"[PhysicianReview] Traitement validé par le médecin : "
                            f"{physician_treatment}"
                )
            ],
        }

    # Pas encore de réponse → interrompre et attendre
    print("   👨‍⚕️ En attente de la revue du médecin...")

    diagnostic_summary = state.get("diagnostic_summary", "N/A")
    interim_care = state.get("interim_care", "N/A")

    return {
        "awaiting_input": "physician",
        "messages": [
            AIMessage(
                content=(
                    f"[PhysicianReview] En attente de la revue du médecin traitant.\n\n"
                    f"── Synthèse clinique ──\n{diagnostic_summary}\n\n"
                    f"── Recommandation intermédiaire ──\n{interim_care}\n\n"
                    f"Le médecin doit proposer un traitement ou une conduite à tenir."
                )
            )
        ],
    }
