"""
graph.py — Graphe LangGraph principal
=======================================
Workflow :
  START → Supervisor → DiagnosticAgent (boucle 5 questions)
  → Supervisor → PhysicianReview (HITL)
  → Supervisor → ReportAgent → Supervisor → END
"""

from langgraph.graph import StateGraph, START, END

from app.state import MedicalState
from app.nodes.supervisor import supervisor_node
from app.nodes.diagnostic_agent import diagnostic_agent_node
from app.nodes.physician_review import physician_review_node
from app.nodes.report_agent import report_agent_node


def route_supervisor(state: dict) -> str:
    """Route conditionnelle après le Supervisor."""
    next_node = state.get("next", "FINISH")
    if next_node == "FINISH":
        return END
    return next_node


def should_interrupt(state: dict) -> str:
    """
    Après le diagnostic_agent ou physician_review,
    vérifie si on doit interrompre (attente d'input humain)
    ou continuer vers le supervisor.
    """
    if state.get("awaiting_input") in ("patient", "physician"):
        return "__interrupt__"
    return "supervisor"


def build_graph() -> StateGraph:
    """Construit et compile le graphe médical."""

    graph = StateGraph(MedicalState)

    # ── Nœuds ──
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("diagnostic_agent", diagnostic_agent_node)
    graph.add_node("physician_review", physician_review_node)
    graph.add_node("report_agent", report_agent_node)

    # ── Arêtes ──
    # START → Supervisor
    graph.add_edge(START, "supervisor")

    # Supervisor → route conditionnelle
    graph.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "diagnostic_agent": "diagnostic_agent",
            "physician_review": "physician_review",
            "report_agent": "report_agent",
            END: END,
        },
    )

    # DiagnosticAgent → vérifie interruption ou supervisor
    graph.add_conditional_edges(
        "diagnostic_agent",
        should_interrupt,
        {
            "__interrupt__": END,   # Sort du graphe (l'API reprendra)
            "supervisor": "supervisor",
        },
    )

    # PhysicianReview → vérifie interruption ou supervisor
    graph.add_conditional_edges(
        "physician_review",
        should_interrupt,
        {
            "__interrupt__": END,
            "supervisor": "supervisor",
        },
    )

    # ReportAgent → Supervisor (pour FINISH)
    graph.add_edge("report_agent", "supervisor")

    return graph.compile()


# Instance compilée (utilisée par l'API et LangGraph Studio)
medical_graph = build_graph()
