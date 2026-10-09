from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_automation_lead():
    response = client.post(
        "/analyze",
        json={
            "company": "Dupont Consulting",
            "contact_name": "Marie Dupont",
            "email": "contact@dupont.fr",
            "employees": 15,
            "message": (
                "Nous cherchons à automatiser le traitement de nos factures. "
                "Budget environ 5 000 €."
            ),
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["category"] == "Business Automation"
    assert result["priority"] == "HIGH"
    assert result["budget_eur"] == 5000


def test_invalid_email_is_rejected():
    response = client.post(
        "/analyze",
        json={
            "company": "Example Company",
            "contact_name": "Test User",
            "email": "not-an-email",
            "employees": 10,
            "message": "We need help automating an internal business process.",
        },
    )
    assert response.status_code == 422
