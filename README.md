# Système Multi-Agents Médical — LangGraph

## Architecture

```
medical-agents/
├── backend/
│   ├── app/
│   │   ├── state.py              # État partagé du graphe
│   │   ├── graph.py              # Graphe LangGraph principal
│   │   ├── nodes/
│   │   │   ├── supervisor.py     # Orchestrateur
│   │   │   ├── diagnostic_agent.py  # Agent de diagnostic
│   │   │   ├── physician_review.py  # Human-in-the-Loop médecin
│   │   │   └── report_agent.py   # Génération du rapport
│   │   ├── tools/
│   │   │   ├── patient_tools.py  # Tools patient (ask_patient)
│   │   │   ├── care_tools.py     # Recommandation intermédiaire
│   │   │   └── mcp_client.py     # Client MCP
│   │   └── api.py                # API FastAPI
│   ├── langgraph.json            # Config LangGraph Studio
│   └── requirements.txt
├── mcp_server/
│   ├── server.py                 # Serveur MCP (drug interaction check)
│   └── data/
│       └── medications.json
├── frontend/
│   └── app.py                    # Interface Streamlit
└── README.md
```

## Installation

```bash
# 1. Installer les dépendances backend
cd backend
pip install -r requirements.txt

# 2. Installer les dépendances MCP
cd ../mcp_server
pip install mcp fastmcp

# 3. Installer Streamlit pour le frontend
pip install streamlit
```

## Configuration

Créez un fichier `.env` dans `backend/` :
```
OPENAI_API_KEY=sk-proj-VOTRE_CLE
```

## Lancement

```bash
# Terminal 1 : Serveur MCP
cd mcp_server && python server.py

# Terminal 2 : API FastAPI
cd backend && uvicorn app.api:app --reload --port 8000

# Terminal 3 : Frontend Streamlit
cd frontend && streamlit run app.py
```

## API Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/sessions/start` | Créer une session |
| POST | `/consultation/start` | Démarrer une consultation |
| POST | `/consultation/resume` | Reprendre (réponse patient / médecin) |
| GET | `/consultation/{thread_id}` | État de la consultation |
| GET | `/consultation/{thread_id}/report` | Rapport final |

## Test LangGraph Studio

```bash
cd backend
langgraph dev
```

## Workflow

```
Patient saisit le cas → Supervisor → DiagnosticAgent (5 questions)
→ Recommandation intermédiaire → Supervisor → PhysicianReview (HITL)
→ Supervisor → ReportAgent → Rapport final
```

## Avertissement

⚠️ Ce système est un exercice académique. Il ne remplace pas une consultation médicale.
