from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import Lead, LeadAnalysis
from services.lead_analyzer import analyze_lead

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
    return analyze_lead(lead)
