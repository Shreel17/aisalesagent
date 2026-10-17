from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == (
        "AI Sales Qualification Agent is running."
    )


def test_price_tool():
    response = client.get("/tools/price")

    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["base_price"] == 15000
    assert data["currency"] == "INR"


def test_budget_eligibility():
    response = client.get("/tools/budget/20000")

    assert response.status_code == 200
    assert response.json()["eligible"] is True


def test_low_budget_is_ineligible():
    response = client.get("/tools/budget/5000")

    assert response.status_code == 200
    assert response.json()["eligible"] is False


def test_complete_lead_is_qualified():
    payload = {
        "lead": {
            "name": "Rahul Sharma",
            "contact": "rahul@example.com",
            "requirements": "Business website development",
            "budget": 20000,
            "timeline": "Within one month",
            "lead_status": "Needs More Information",
            "missing_information": [],
            "qualification_reason": ""
        }
    }

    response = client.post("/qualify", json=payload)

    assert response.status_code == 200
    assert response.json()["lead_status"] == "Qualified"


def test_missing_details_need_more_information():
    payload = {
        "lead": {
            "name": "Priya Patel",
            "contact": None,
            "requirements": "Business website development",
            "budget": 20000,
            "timeline": None,
            "lead_status": "Needs More Information",
            "missing_information": [],
            "qualification_reason": ""
        }
    }

    response = client.post("/qualify", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["lead_status"] == "Needs More Information"
    assert "contact" in data["missing_information"]
    assert "timeline" in data["missing_information"]


def test_low_budget_lead_is_unqualified():
    payload = {
        "lead": {
            "name": "Amit Patel",
            "contact": "amit@example.com",
            "requirements": "Business website development",
            "budget": 5000,
            "timeline": "Within two weeks",
            "lead_status": "Needs More Information",
            "missing_information": [],
            "qualification_reason": ""
        }
    }

    response = client.post("/qualify", json=payload)

    assert response.status_code == 200
    assert response.json()["lead_status"] == "Unqualified"