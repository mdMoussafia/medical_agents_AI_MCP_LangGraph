"""
diagnostic_agent.py — Agent de Diagnostic
===========================================
Pose 5 questions au patient, produit une synthèse clinique
préliminaire et une recommandation intermédiaire.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Questions médicales de base à adapter selon le cas
BASE_QUESTIONS = [
    "Depuis combien de temps ressentez-vous ces symptômes ?",
    "Pouvez-vous décrire la douleur ou la gêne (localisation, intensité de 1 à 10) ?",
    "Avez-vous d'autres symptômes associés (fièvre, fatigue, nausées, etc.) ?",
    "Prenez-vous actuellement des médicaments ou avez-vous des allergies connues ?",
    "Avez-vous des antécédents médicaux ou chirurgicaux importants ?",
]


def diagnostic_agent_node(state: dict) -> dict:
    """
    Logique du Diagnostic Agent :
    - Si < 5 questions posées : générer et poser la prochaine question
    - Si 5 questions posées : produire la synthèse + recommandation intermédiaire
    """
    question_count = state.get("question_count", 0)
    questions = list(state.get("questions", []))
    answers = list(state.get("answers", []))
    patient_case = state.get("patient_case", "")

    # ── Phase 1 : Poser des questions (< 5) ──
    if question_count < 5:
        # Générer une question contextuelle via le LLM
        context = f"Cas patient : {patient_case}\n"
        if questions:
            qa_history = "\n".join(
                f"Q{i+1}: {q}\nR{i+1}: {a}"
                for i, (q, a) in enumerate(zip(questions, answers))
            )
            context += f"Historique Q/R :\n{qa_history}\n"

        prompt = (
            f"Tu es un agent de pré-diagnostic médical. "
            f"Tu dois poser exactement 5 questions au patient.\n\n"
            f"{context}\n"
            f"C'est la question numéro {question_count + 1}/5.\n"
            f"Voici une suggestion : \"{BASE_QUESTIONS[question_count]}\"\n\n"
            f"Adapte cette question au contexte du patient si nécessaire. "
            f"Retourne UNIQUEMENT la question, rien d'autre."
        )

        response = llm.invoke([HumanMessage(content=prompt)])
        question = response.content.strip()

        questions.append(question)

        print(f"   🩺 Question {question_count + 1}/5 : {question}")

        return {
            "questions": questions,
            "question_count": question_count,  # Pas encore incrémenté (attente réponse)
            "current_question": question,
            "awaiting_input": "patient",
            "messages": [AIMessage(content=f"[DiagnosticAgent] Question {question_count + 1}/5 : {question}")],
        }

    # ── Phase 2 : Synthèse clinique (5 questions posées) ──
    qa_text = "\n".join(
        f"Q{i+1}: {q}\nR{i+1}: {a}"
        for i, (q, a) in enumerate(zip(questions, answers))
    )

    # Synthèse clinique
    summary_prompt = (
        f"Tu es un agent de pré-diagnostic. Produis une SYNTHÈSE CLINIQUE PRÉLIMINAIRE "
        f"basée sur les informations suivantes.\n\n"
        f"Cas initial : {patient_case}\n\n"
        f"Questions et réponses :\n{qa_text}\n\n"
        f"Produis :\n"
        f"1. Un résumé des symptômes principaux\n"
        f"2. Les facteurs de risque identifiés\n"
        f"3. Les orientations cliniques possibles (PAS de diagnostic définitif)\n\n"
        f"⚠️ Termine par : 'Ce système ne remplace pas une consultation médicale.'"
    )

    summary_resp = llm.invoke([HumanMessage(content=summary_prompt)])
    diagnostic_summary = summary_resp.content.strip()

    # Recommandation intermédiaire
    care_prompt = (
        f"Basé sur cette synthèse clinique :\n{diagnostic_summary}\n\n"
        f"Génère une RECOMMANDATION INTERMÉDIAIRE prudente. "
        f"Inclus : repos, hydratation, surveillance, et quand consulter. "
        f"Indique le niveau de sévérité estimé (faible/modéré/élevé). "
        f"⚠️ Précise que cela ne remplace pas l'avis d'un médecin."
    )

    care_resp = llm.invoke([HumanMessage(content=care_prompt)])
    interim_care = care_resp.content.strip()

    print("   🩺 Synthèse clinique et recommandation générées")

    return {
        "diagnostic_summary": diagnostic_summary,
        "interim_care": interim_care,
        "awaiting_input": "",
        "messages": [
            AIMessage(content=f"[DiagnosticAgent] Synthèse clinique :\n{diagnostic_summary}"),
            AIMessage(content=f"[DiagnosticAgent] Recommandation intermédiaire :\n{interim_care}"),
        ],
    }
