"""
report_agent.py — Agent de Génération du Rapport Final
========================================================
Compile toutes les informations en un rapport structuré.
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def report_agent_node(state: dict) -> dict:
    """
    Génère le rapport final structuré à partir de toutes les données :
    - Cas patient initial
    - Questions / réponses
    - Synthèse clinique
    - Recommandation intermédiaire
    - Traitement du médecin
    """
    patient_case = state.get("patient_case", "N/A")
    questions = state.get("questions", [])
    answers = state.get("answers", [])
    diagnostic_summary = state.get("diagnostic_summary", "N/A")
    interim_care = state.get("interim_care", "N/A")
    physician_treatment = state.get("physician_treatment", "N/A")

    qa_section = "\n".join(
        f"  Q{i+1}: {q}\n  R{i+1}: {a}"
        for i, (q, a) in enumerate(zip(questions, answers))
    )

    report_prompt = (
        f"Tu es un agent de rédaction médicale. Génère un RAPPORT FINAL STRUCTURÉ "
        f"en français, avec les sections suivantes :\n\n"
        f"1. EN-TÊTE avec la date\n"
        f"2. MOTIF DE CONSULTATION\n"
        f"3. ANAMNÈSE (questions/réponses)\n"
        f"4. SYNTHÈSE CLINIQUE PRÉLIMINAIRE\n"
        f"5. RECOMMANDATION INTERMÉDIAIRE\n"
        f"6. AVIS DU MÉDECIN TRAITANT\n"
        f"7. CONDUITE À TENIR\n"
        f"8. AVERTISSEMENT LÉGAL\n\n"
        f"── Données ──\n"
        f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        f"Cas initial : {patient_case}\n\n"
        f"Questions / Réponses :\n{qa_section}\n\n"
        f"Synthèse clinique : {diagnostic_summary}\n\n"
        f"Recommandation intermédiaire : {interim_care}\n\n"
        f"Avis du médecin : {physician_treatment}\n\n"
        f"⚠️ Le rapport DOIT contenir la mention : "
        f"'Ce système ne remplace pas une consultation médicale.'\n"
        f"⚠️ Le rapport DOIT préciser qu'il s'agit d'un exercice académique."
    )

    response = llm.invoke([HumanMessage(content=report_prompt)])
    final_report = response.content.strip()

    print("   📋 Rapport final généré")

    return {
        "final_report": final_report,
        "awaiting_input": "",
        "messages": [
            AIMessage(content=f"[ReportAgent] Rapport final généré.")
        ],
    }
