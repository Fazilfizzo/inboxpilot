def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "InboxPilot API",
    }


def test_classify_payment_email(client):
    payload = {
        "sender": "customer@gmail.com",
        "subject": "Payment problem",
        "body": (
            "I was charged twice and this is unacceptable. Please resolve immediately."
        ),
    }

    response = client.post(
        "/api/v1/emails/classify",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["category"] == "payment_issue"
    assert data["priority"] == "high"
    assert data["sentiment"] == "negative"
    assert data["requires_human"] is True


def test_classify_general_email(client):
    payload = {
        "sender": "customer@gmail.com",
        "subject": "Product information",
        "body": "I would like to know more about your products.",
    }

    response = client.post(
        "/api/v1/emails/classify",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["category"] == "general"
    assert data["priority"] == "low"
    assert data["sentiment"] == "neutral"
    assert data["requires_human"] is False


def test_classify_rejects_invalid_email(client):
    payload = {
        "sender": "not-an-email",
        "subject": "Payment problem",
        "body": "I need help with my payment.",
    }

    response = client.post(
        "/api/v1/emails/classify",
        json=payload,
    )

    assert response.status_code == 422


def test_classify_rejects_missing_subject(client):
    payload = {
        "sender": "customer@gmail.com",
        "body": "I need help with my payment.",
    }

    response = client.post(
        "/api/v1/emails/classify",
        json=payload,
    )

    assert response.status_code == 422


def test_classify_rejects_short_subject(client):
    payload = {
        "sender": "customer@gmail.com",
        "subject": "A",
        "body": "I need help with my payment.",
    }

    response = client.post(
        "/api/v1/emails/classify",
        json=payload,
    )

    assert response.status_code == 422


def test_classify_rejects_short_body(client):
    payload = {
        "sender": "customer@gmail.com",
        "subject": "Payment problem",
        "body": "Help",
    }

    response = client.post(
        "/api/v1/emails/classify",
        json=payload,
    )

    assert response.status_code == 422


def test_classify_rejects_empty_request(client):
    response = client.post(
        "/api/v1/emails/classify",
        json={},
    )

    assert response.status_code == 422
