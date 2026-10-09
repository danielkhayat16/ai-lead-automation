import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib import request

from models import Lead, LeadAnalysis

DB_PATH = Path(os.getenv("LEADS_DB_PATH", Path(__file__).resolve().parent.parent / "leads.db"))


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        company TEXT NOT NULL,
        contact_name TEXT NOT NULL,
        email TEXT NOT NULL,
        employees INTEGER,
        message TEXT NOT NULL,
        analysis_json TEXT NOT NULL
        )"""
    )
    return conn


def save_lead(lead: Lead, analysis: LeadAnalysis) -> int:
    with _connect() as conn:
        cur = conn.execute(
            """INSERT INTO leads
            (created_at, company, contact_name, email, employees, message, analysis_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                datetime.now(timezone.utc).isoformat(),
                lead.company, lead.contact_name, str(lead.email),
                lead.employees, lead.message, analysis.model_dump_json(),
            ),
        )
        return int(cur.lastrowid)


def list_leads() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM leads ORDER BY id DESC LIMIT 100").fetchall()
    return [
        {
            "id": row["id"], "created_at": row["created_at"], "company": row["company"],
            "contact_name": row["contact_name"], "email": row["email"],
            "employees": row["employees"], "message": row["message"],
            "analysis": json.loads(row["analysis_json"]),
        }
        for row in rows
    ]


def send_to_n8n(lead_id: int, lead: Lead, analysis: LeadAnalysis) -> bool:
    url = os.getenv("N8N_WEBHOOK_URL")
    if not url:
        return False
    payload = json.dumps({
        "lead_id": lead_id,
        "lead": lead.model_dump(mode="json"),
        "analysis": analysis.model_dump(mode="json"),
    }).encode("utf-8")
    req = request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with request.urlopen(req, timeout=10) as response:
            return 200 <= response.status < 300
    except Exception:
        return False
