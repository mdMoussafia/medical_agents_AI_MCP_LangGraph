"""
care_tools.py — Tool de recommandation intermédiaire
=====================================================
"""

from langchain_core.tools import tool


@tool
def recommend_interim_care(symptoms: str, severity: str) -> str:
    """Génère une recommandation intermédiaire prudente basée sur les symptômes.
    Cette recommandation ne remplace PAS l'avis d'un médecin.

    Args:
        symptoms: Résumé des symptômes principaux du patient.
        severity: Niveau de sévérité estimé ('faible', 'modéré', 'élevé').
    Returns:
        Recommandation intermédiaire de soins.
    """
    base_recs = [
        "Repos et hydratation régulière.",
        "Surveillance des symptômes toutes les 4 à 6 heures.",
        "Consultation médicale recommandée si aggravation.",
    ]

    if severity.lower() in ("élevé", "eleve", "high"):
        base_recs.insert(0, "⚠️ RED FLAG DÉTECTÉ — Consultation médicale urgente recommandée.")
        base_recs.append("Ne pas attendre : se rendre aux urgences si dégradation rapide.")
    elif severity.lower() in ("modéré", "modere", "moderate"):
        base_recs.append("Prendre rendez-vous avec un médecin dans les 24-48h.")
    else:
        base_recs.append("Repos à domicile, reconsulter si pas d'amélioration sous 3 jours.")

    care = (
        f"RECOMMANDATION INTERMÉDIAIRE (non-définitive)\n"
        f"Symptômes identifiés : {symptoms}\n"
        f"Sévérité estimée : {severity}\n\n"
        f"Conseils :\n" + "\n".join(f"  • {r}" for r in base_recs) + "\n\n"
        f"⚠️ Ce système ne remplace pas une consultation médicale."
    )
    return care
