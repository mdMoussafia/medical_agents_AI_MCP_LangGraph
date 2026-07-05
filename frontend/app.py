"""
app.py — Frontend Streamlit pour le système multi-agents médical
==================================================================
Interface utilisateur avec 4 écrans :
  1. Saisie du cas patient
  2. Questions / réponses patient
  3. Revue médecin (traitement)
  4. Rapport final
"""

import streamlit as st
import requests

API_URL = "http://localhost:8000"

# ── Configuration de la page ──
st.set_page_config(
    page_title="Système Multi-Agents Médical",
    page_icon="🏥",
    layout="centered",
)


def init_session():
    """Initialise les variables de session Streamlit."""
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None
    if "stage" not in st.session_state:
        st.session_state.stage = "start"  # start, questions, physician, report
    if "current_question" not in st.session_state:
        st.session_state.current_question = ""
    if "question_count" not in st.session_state:
        st.session_state.question_count = 0
    if "qa_history" not in st.session_state:
        st.session_state.qa_history = []
    if "diagnostic_summary" not in st.session_state:
        st.session_state.diagnostic_summary = ""
    if "interim_care" not in st.session_state:
        st.session_state.interim_care = ""
    if "final_report" not in st.session_state:
        st.session_state.final_report = ""


init_session()

# ── En-tête ──
st.title("🏥 Système Multi-Agents Médical")
st.caption("Orientation clinique préliminaire — Exercice académique")
st.divider()


# ══════════════════════════════════════════════
#  ÉCRAN 1 : Saisie du cas patient
# ══════════════════════════════════════════════

if st.session_state.stage == "start":
    st.header("📋 Écran 1 — Nouveau Cas Patient")

    st.warning(
        "⚠️ Ce système est un exercice académique. "
        "Il ne remplace pas une consultation médicale."
    )

    patient_case = st.text_area(
        "Décrivez le cas du patient :",
        placeholder="Ex: Patient de 45 ans, homme, présente une toux sèche "
                    "depuis 5 jours avec fièvre modérée (38.2°C) et fatigue.",
        height=150,
    )

    if st.button("🚀 Démarrer la consultation", type="primary", disabled=not patient_case):
        with st.spinner("Création de la session..."):
            # Créer la session
            resp = requests.post(f"{API_URL}/sessions/start")
            if resp.status_code != 200:
                st.error("Erreur lors de la création de la session")
                st.stop()

            thread_id = resp.json()["thread_id"]
            st.session_state.thread_id = thread_id

            # Démarrer la consultation
            resp = requests.post(
                f"{API_URL}/consultation/start",
                json={"thread_id": thread_id, "patient_case": patient_case},
            )
            if resp.status_code != 200:
                st.error(f"Erreur : {resp.text}")
                st.stop()

            data = resp.json()
            st.session_state.current_question = data.get("current_question", "")
            st.session_state.question_count = data.get("question_count", 0)
            st.session_state.stage = "questions"
            st.rerun()


# ══════════════════════════════════════════════
#  ÉCRAN 2 : Questions / Réponses Patient
# ══════════════════════════════════════════════

elif st.session_state.stage == "questions":
    st.header("🩺 Écran 2 — Questions au Patient")

    # Afficher l'historique Q/R
    if st.session_state.qa_history:
        for i, (q, a) in enumerate(st.session_state.qa_history, 1):
            st.info(f"**Question {i}** : {q}")
            st.success(f"**Réponse** : {a}")

    # Question courante
    q_num = len(st.session_state.qa_history) + 1
    if st.session_state.current_question:
        st.info(f"**Question {q_num}/5** : {st.session_state.current_question}")

        answer = st.text_input(
            "Votre réponse :",
            key=f"answer_{q_num}",
            placeholder="Tapez votre réponse ici...",
        )

        if st.button("📨 Envoyer la réponse", type="primary", disabled=not answer):
            with st.spinner("Traitement en cours..."):
                # Sauvegarder dans l'historique local
                st.session_state.qa_history.append(
                    (st.session_state.current_question, answer)
                )

                # Envoyer au backend
                resp = requests.post(
                    f"{API_URL}/consultation/resume",
                    json={
                        "thread_id": st.session_state.thread_id,
                        "input_type": "patient",
                        "content": answer,
                    },
                )

                if resp.status_code != 200:
                    st.error(f"Erreur : {resp.text}")
                    st.stop()

                data = resp.json()

                if data.get("awaiting_input") == "patient":
                    # Encore des questions
                    st.session_state.current_question = data.get("current_question", "")
                    st.session_state.question_count = data.get("question_count", 0)
                elif data.get("awaiting_input") == "physician":
                    # Phase médecin
                    st.session_state.diagnostic_summary = data.get("diagnostic_summary", "")
                    st.session_state.interim_care = data.get("interim_care", "")
                    st.session_state.stage = "physician"
                elif data.get("has_report"):
                    st.session_state.stage = "report"

                st.rerun()

    # Barre de progression
    progress = len(st.session_state.qa_history) / 5
    st.progress(progress, text=f"Questions : {len(st.session_state.qa_history)}/5")


# ══════════════════════════════════════════════
#  ÉCRAN 3 : Revue Médecin (HITL)
# ══════════════════════════════════════════════

elif st.session_state.stage == "physician":
    st.header("👨‍⚕️ Écran 3 — Revue du Médecin Traitant")

    st.info("Le médecin traitant doit examiner la synthèse et proposer un traitement.")

    # Afficher la synthèse clinique
    with st.expander("📄 Synthèse clinique préliminaire", expanded=True):
        st.write(st.session_state.diagnostic_summary)

    # Afficher la recommandation intermédiaire
    with st.expander("💊 Recommandation intermédiaire", expanded=True):
        st.write(st.session_state.interim_care)

    st.divider()

    # Saisie du traitement par le médecin
    st.subheader("Traitement / Conduite à tenir")
    treatment = st.text_area(
        "Proposez un traitement ou une conduite à tenir :",
        placeholder="Ex: Prescription de paracétamol 1g x3/jour pendant 5 jours. "
                    "Repos 48h. Contrôle si fièvre persistante au-delà de 72h.",
        height=150,
    )

    if st.button("✅ Valider le traitement", type="primary", disabled=not treatment):
        with st.spinner("Génération du rapport final..."):
            resp = requests.post(
                f"{API_URL}/consultation/resume",
                json={
                    "thread_id": st.session_state.thread_id,
                    "input_type": "physician",
                    "content": treatment,
                },
            )

            if resp.status_code != 200:
                st.error(f"Erreur : {resp.text}")
                st.stop()

            st.session_state.stage = "report"
            st.rerun()


# ══════════════════════════════════════════════
#  ÉCRAN 4 : Rapport Final
# ══════════════════════════════════════════════

elif st.session_state.stage == "report":
    st.header("📋 Écran 4 — Rapport Final")

    # Récupérer le rapport
    if not st.session_state.final_report:
        with st.spinner("Chargement du rapport..."):
            resp = requests.get(
                f"{API_URL}/consultation/{st.session_state.thread_id}/report"
            )
            if resp.status_code == 200:
                st.session_state.final_report = resp.json()["report"]
            else:
                st.error("Le rapport n'est pas encore disponible.")
                st.stop()

    # Afficher le rapport
    st.markdown(st.session_state.final_report)

    st.divider()
    st.warning(
        "⚠️ **AVERTISSEMENT** : Ce système est un exercice académique. "
        "Ce rapport ne constitue pas un avis médical. "
        "Ce système ne remplace pas une consultation médicale."
    )

    # Boutons d'action
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Nouvelle consultation"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    with col2:
        st.download_button(
            "📥 Télécharger le rapport",
            data=st.session_state.final_report,
            file_name="rapport_medical.txt",
            mime="text/plain",
        )


# ── Sidebar ──
with st.sidebar:
    st.header("ℹ️ Informations")
    if st.session_state.thread_id:
        st.code(f"Session : {st.session_state.thread_id}")
        st.write(f"Étape : **{st.session_state.stage}**")

    st.divider()
    st.caption(
        "Projet académique — Système multi-agents\n"
        "LangGraph · FastAPI · Streamlit\n\n"
        "Ce système ne remplace pas une consultation médicale."
    )
