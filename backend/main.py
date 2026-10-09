from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from models import Lead, LeadAnalysis
from lead_store import list_leads, save_lead, send_to_n8n
from services.lead_analyzer import analyze_lead

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"

app = FastAPI(
    title="AI Lead Automation API",
    description="Analyze inbound business leads and return structured sales data.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze", response_model=LeadAnalysis)
def analyze(lead: Lead) -> LeadAnalysis:
    analysis = analyze_lead(lead)
    lead_id = save_lead(lead, analysis)
    send_to_n8n(lead_id, lead, analysis)
    return analysis


@app.get("/leads")
def leads() -> list[dict]:
    return list_leads()


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
def frontend() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")
