# AI Lead Automation

A portfolio project demonstrating how an inbound business lead can be transformed into structured, actionable sales data.

## What it does

A visitor submits a lead through a web form. A Python/FastAPI backend validates the request and returns:

- lead category
- priority
- detected budget
- normalized business need
- short summary
- suggested next action

The first version deliberately uses a deterministic analyzer so the whole project works without paid APIs or secrets. The next iteration will add an LLM provider behind the same API contract.

## Architecture

```text
Web form
   |
   v
FastAPI / Python
   |
   v
Lead validation
   |
   v
Analyzer
   |
   v
Structured JSON
   |
   +--> Browser result
   +--> Future: n8n / CRM / email
```

## Run locally

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open `frontend/index.html` in a browser and submit the pre-filled sample lead.

API docs are available locally at `/docs`.

## Example

Input:

```json
{
  "company": "Dupont Consulting",
  "contact_name": "Marie Dupont",
  "email": "contact@dupont.fr",
  "employees": 15,
  "message": "Nous cherchons à automatiser le traitement de nos factures. Budget environ 5 000 €."
}
```

Expected analysis includes **Business Automation**, **HIGH** priority and a detected budget of **€5,000**.

## Roadmap

- [x] FastAPI backend
- [x] Lead validation
- [x] Deterministic lead analyzer
- [x] Browser demo UI
- [ ] LLM-powered analysis
- [ ] n8n workflow
- [ ] CRM / lead storage
- [ ] Automated email action
- [ ] Public deployment

## Author

Daniel Khayat — Software Developer · Automation · APIs · AI

daniel.khayat8@gmail.com
