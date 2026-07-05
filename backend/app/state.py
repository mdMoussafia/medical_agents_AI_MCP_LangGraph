"""
state.py — État partagé du graphe médical
==========================================
Toutes les données transitent via cet état.
"""

from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class MedicalState(TypedDict, total=False):
    """État partagé entre tous les nœuds du graphe."""

    # Messages LangGraph (historique de la conversation interne)
    messages: Annotated[list, add_messages]

    # Routage : le Supervisor décide du prochain nœud
    next: Literal[
        "diagnostic_agent",
        "physician_review",
        "report_agent",
        "FINISH",
    ]

    # ── Données patient ──
    patient_case: str           # Description initiale du cas
    questions: list[str]        # Questions posées par le DiagnosticAgent
    answers: list[str]          # Réponses du patient
    question_count: int         # Compteur de questions (objectif : 5)

    # ── Résultats cliniques ──
    diagnostic_summary: str     # Synthèse clinique préliminaire
    interim_care: str           # Recommandation intermédiaire

    # ── Médecin (HITL) ──
    physician_treatment: str    # Traitement proposé par le médecin

    # ── Rapport ──
    final_report: str           # Rapport final structuré

    # ── Contrôle de flux ──
    awaiting_input: str         # "patient" | "physician" | "" (pour le frontend)
    current_question: str       # Question en cours pour le patient
