"""
patient_tools.py — Tool pour poser des questions au patient
============================================================
"""

from langchain_core.tools import tool


@tool
def ask_patient(question: str) -> str:
    """Pose une question au patient et attend sa réponse.
    Cette fonction enregistre la question. La réponse sera fournie
    via le mécanisme Human-in-the-Loop du frontend.

    Args:
        question: La question médicale à poser au patient.
    Returns:
        Confirmation que la question a été enregistrée.
    """
    return f"QUESTION_POSÉE: {question}"
