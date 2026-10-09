import json
import os
import re
from urllib import error, request

from models import Lead, LeadAnalysis


AUTOMATION_WORDS = {
    "automate", "automation", "automatiser", "automatisation",
    "workflow", "facture", "invoice", "crm", "api",
}


def _extract_budget(message: str) -> int | None:
    normalized = message.lower().replace("\u202f", " ").replace("\xa0", " ")
    patterns = [
        r"(\d{1,3}(?:[ .]\d{3})+)\s*(?:€|eur|euros?)",
        r"(\d+)\s*k\s*(?:€|eur|euros?)?",
    ]
    for index, pattern in enumerate(patterns):
        match = re.search(pattern, normalized)
        if match:
            raw = match.group(1).replace(" ", "").replace(".", "")
            value = int(raw)
            return value * 1000 if index == 1 else value
    return None


def _fallback_analysis(lead: Lead) -> LeadAnalysis:
    text = lead.message.lower()
    budget = _extract_budget(lead.message)
    is_automation = any(word in text for word in AUTOMATION_WORDS)
    category = "Business Automation" if is_automation else "Software Development"

    if budget and budget >= 5000:
        priority = "HIGH"
    elif budget and budget >= 1500:
        priority = "MEDIUM"
    else:
        priority = "MEDIUM" if is_automation else "LOW"

    need = "Automate a business process" if is_automation else "Custom software or technical support"
    employee_text = f" with {lead.employees} employees" if lead.employees is not None else ""
    summary = (
        f"{lead.company}{employee_text} is looking for {need.lower()}."
        + (f" Stated budget: €{budget:,}." if budget else "")
    )
    action = (
        "Schedule a discovery call and map the current workflow."
        if priority == "HIGH"
        else "Review the requirements and request any missing technical details."
    )
    return LeadAnalysis(
        company=lead.company, category=category, priority=priority,
        budget_eur=budget, need=need, summary=summary, suggested_action=action,
    )


def _llm_analysis(lead: Lead, api_key: str) -> LeadAnalysis:
    model = os.getenv("OPENAI_MODEL", "gpt-5-mini")
    schema = LeadAnalysis.model_json_schema()
    prompt = (
        "Analyze this inbound sales lead. Return concise, useful sales qualification. "
        "Priority must reflect commercial urgency, clarity and budget. "
        f"Lead: {lead.model_dump_json()}"
    )
    payload = {
        "model": model,
        "input": [
            {"role": "system", "content": "You qualify software, automation and AI project leads."},
            {"role": "user", "content": prompt},
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "lead_analysis",
                "strict": True,
                "schema": schema,
            }
        },
    }
    req = request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=20) as response:
        body = json.loads(response.read())
    return LeadAnalysis.model_validate_json(body["output"][0]["content"][0]["text"])


def analyze_lead(lead: Lead) -> LeadAnalysis:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _fallback_analysis(lead)
    try:
        return _llm_analysis(lead, api_key)
    except (error.URLError, TimeoutError, KeyError, ValueError):
        return _fallback_analysis(lead)
