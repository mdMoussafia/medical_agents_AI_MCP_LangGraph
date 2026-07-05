"""
supervisor.py — Agent Superviseur (Orchestrateur)
===================================================
Décide quel agent exécuter à chaque étape du workflow.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def supervisor_node(state: dict) -> dict:
    """
    Le Supervisor orchestre le workflow :
    1. Si pas encore de diagnostic → diagnostic_agent
    2. Si diagnostic fait mais pas de revue médecin → physician_review
    3. Si revue médecin faite → report_agent
    4. Si rapport fait → FINISH
    """
    diagnostic_summary = state.get("diagnostic_summary", "")
    physician_treatment = state.get("physician_treatment", "")
    final_report = state.get("final_report", "")
    question_count = state.get("question_count", 0)

    # Si le rapport est déjà généré → Terminé
    if final_report:
        print("   🟢 Supervisor → FINISH")
        return {"next": "FINISH"}

    # Si le médecin a donné son traitement → générer le rapport
    if physician_treatment:
        print("   🟢 Supervisor → report_agent")
        return {"next": "report_agent"}

    # Si le diagnostic est fait (5 questions posées + synthèse) → médecin
    if diagnostic_summary and question_count >= 5:
        print("   🟢 Supervisor → physician_review")
        return {"next": "physician_review"}

    # Sinon → continuer le diagnostic
    print("   🟢 Supervisor → diagnostic_agent")
    return {"next": "diagnostic_agent"}
