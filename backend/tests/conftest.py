import pytest
from fastapi.testclient import TestClient

from app.main import app

# Answers for an in-scope, non-prohibited provider path reaching the end of
# the questionnaire with minimal risk.
MINIMAL = {
    "role": "provider",
    "is_ai_system": True,
    "eu_nexus": True,
    "exclusion": "none",
    "prohibited_practices": ["none"],
    "gpai_model": False,
    "annex_i_product": False,
    "annex_iii_uses": ["none"],
    "transparency_cases": ["none"],
    "human_oversight": "in_the_loop",
    "scale": "small",
    "vulnerable_groups": False,
    "personal_data": "none",
}


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def answers(**overrides):
    return {**MINIMAL, **overrides}
