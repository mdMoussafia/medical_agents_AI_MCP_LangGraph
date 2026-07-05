"""
api.py — API FastAPI pour le système multi-agents médical
===========================================================
Endpoints :
  POST /sessions/start          → Créer une session
  POST /consultation/start      → Démarrer une consultation
  POST /consultation/resume     → Reprendre (réponse patient / médecin)
  GET  /consultation/{id}       → État courant
  GET  /consultation/{id}/report → Rapport final
"""

import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.graph import medical_graph

app = FastAPI(
    title="Système Multi-Agents Médical",
    description="API pour le workflow d'orientation clinique préliminaire",
    version="1.0.0",
)

# CORS pour le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Stockage en mémoire des sessions ──
sessions: dict[str, dict] = {}


# ── Modèles Pydantic ──

class SessionResponse(BaseModel):
    thread_id: str
    message: str


class StartConsultationRequest(BaseModel):
    thread_id: str
    patient_case: str


class ResumeRequest(BaseModel):
    thread_id: str
    input_type: str   # "patient" ou "physician"
    content: str      # Réponse du patient ou traitement du médecin


class ConsultationStatus(BaseModel):
    thread_id: str
    status: str
    awaiting_input: str
    question_count: int
    current_question: str
    diagnostic_summary: str
    interim_care: str
    physician_treatment: str
    has_report: bool


# ── Endpoints ──

@app.post("/sessions/start", response_model=SessionResponse)
def start_session():
    """Crée une nouvelle session de consultation."""
    thread_id = str(uuid.uuid4())[:8]
    sessions[thread_id] = {
        "messages": [],
        "next": "diagnostic_agent",
        "patient_case": "",
        "questions": [],
        "answers": [],
        "question_count": 0,
        "diagnostic_summary": "",
        "interim_care": "",
        "physician_treatment": "",
        "final_report": "",
        "awaiting_input": "",
        "current_question": "",
    }
    return SessionResponse(thread_id=thread_id, message="Session créée")


@app.post("/consultation/start")
def start_consultation(req: StartConsultationRequest):
    """Démarre le workflow de consultation avec le cas patient."""
    if req.thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session non trouvée")

    state = sessions[req.thread_id]
    state["patient_case"] = req.patient_case

    # Exécuter le graphe
    result = medical_graph.invoke(state)
    sessions[req.thread_id] = dict(result)

    return _format_response(req.thread_id, result)


@app.post("/consultation/resume")
def resume_consultation(req: ResumeRequest):
    """Reprend le workflow après une réponse patient ou médecin."""
    if req.thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session non trouvée")

    state = sessions[req.thread_id]

    if req.input_type == "patient":
        # Ajouter la réponse du patient
        answers = list(state.get("answers", []))
        answers.append(req.content)
        state["answers"] = answers
        state["question_count"] = len(answers)
        state["awaiting_input"] = ""

    elif req.input_type == "physician":
        # Ajouter le traitement du médecin
        state["physician_treatment"] = req.content
        state["awaiting_input"] = ""

    else:
        raise HTTPException(status_code=400, detail="input_type doit être 'patient' ou 'physician'")

    # Reprendre le graphe
    result = medical_graph.invoke(state)
    sessions[req.thread_id] = dict(result)

    return _format_response(req.thread_id, result)


@app.get("/consultation/{thread_id}", response_model=ConsultationStatus)
def get_consultation(thread_id: str):
    """Retourne l'état courant de la consultation."""
    if thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session non trouvée")

    state = sessions[thread_id]
    return ConsultationStatus(
        thread_id=thread_id,
        status="completed" if state.get("final_report") else "in_progress",
        awaiting_input=state.get("awaiting_input", ""),
        question_count=state.get("question_count", 0),
        current_question=state.get("current_question", ""),
        diagnostic_summary=state.get("diagnostic_summary", ""),
        interim_care=state.get("interim_care", ""),
        physician_treatment=state.get("physician_treatment", ""),
        has_report=bool(state.get("final_report")),
    )


@app.get("/consultation/{thread_id}/report")
def get_report(thread_id: str):
    """Retourne le rapport final."""
    if thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session non trouvée")

    state = sessions[thread_id]
    report = state.get("final_report", "")

    if not report:
        raise HTTPException(status_code=400, detail="Rapport non encore généré")

    return {
        "thread_id": thread_id,
        "report": report,
        "disclaimer": "Ce système ne remplace pas une consultation médicale.",
    }


def _format_response(thread_id: str, state: dict) -> dict:
    """Formate la réponse API."""
    return {
        "thread_id": thread_id,
        "status": "completed" if state.get("final_report") else "in_progress",
        "awaiting_input": state.get("awaiting_input", ""),
        "current_question": state.get("current_question", ""),
        "question_count": state.get("question_count", 0),
        "diagnostic_summary": state.get("diagnostic_summary", ""),
        "interim_care": state.get("interim_care", ""),
        "has_report": bool(state.get("final_report")),
    }
