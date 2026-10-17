from .conftest import answers

PROFILE = {"system_name": "Tri de CV <Beta>", "organization": "ACME & Cie", "description": "Présélection des candidatures."}


def walk(client, choose):
    """Drive the questionnaire through /next, answering with `choose`."""
    collected = {}
    progress = []
    while True:
        response = client.post("/api/v1/diagnostic/next", json={"answers": collected})
        assert response.status_code == 200
        body = response.json()
        progress.append(body["progress"])
        if body["done"]:
            return collected, progress
        question = body["question"]
        collected[question["id"]] = choose(question)


def test_health(client):
    assert client.get("/api/v1/health").json() == {"status": "ok"}


def test_questionnaire_lists_questions(client):
    questions = client.get("/api/v1/diagnostic/questionnaire").json()
    assert questions[0]["id"] == "role"
    assert len(questions) == 17


def test_full_flow_high_risk(client):
    target = answers(annex_iii_uses=["recruitment"], profiling=True)
    collected, progress = walk(client, lambda q: target[q["id"]])
    assert collected == {k: v for k, v in target.items()}
    assert progress[-1] == 1.0
    assert progress == sorted(progress)

    result = client.post("/api/v1/diagnostic/assess", json={"profile": PROFILE, "answers": collected}).json()
    assert result["category"] == "high"
    assert result["category_label"] == "Haut risque"


def test_report_returns_pdf(client):
    response = client.post(
        "/api/v1/diagnostic/report",
        json={"profile": PROFILE, "answers": answers(annex_iii_uses=["recruitment"], profiling=True, transparency_cases=["direct_interaction"])},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"] == 'attachment; filename="diagnostic-ai-act-tri-de-cv-beta.pdf"'
    assert response.content.startswith(b"%PDF")


def test_report_for_out_of_scope_system(client):
    response = client.post("/api/v1/diagnostic/report", json={"profile": {"system_name": "Règles"}, "answers": {"role": "deployer", "is_ai_system": False}})
    assert response.status_code == 200
    assert response.content.startswith(b"%PDF")


def test_incomplete_questionnaire_is_rejected(client):
    response = client.post("/api/v1/diagnostic/assess", json={"profile": PROFILE, "answers": {"role": "provider"}})
    assert response.status_code == 422
    assert "pas terminé" in response.json()["detail"]


def test_invalid_answer_is_rejected(client):
    response = client.post("/api/v1/diagnostic/next", json={"answers": {"role": "ceo"}})
    assert response.status_code == 422


def test_missing_system_name_is_rejected(client):
    response = client.post("/api/v1/diagnostic/assess", json={"profile": {"system_name": ""}, "answers": answers()})
    assert response.status_code == 422
