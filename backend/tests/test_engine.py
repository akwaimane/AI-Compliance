import pytest

from app.diagnostic.engine import assess
from app.diagnostic.models import RiskCategory
from app.diagnostic.questionnaire import next_question

from .conftest import answers


def codes(result):
    return [o.code for o in result.obligations]


def test_minimal_risk():
    result = assess(answers())
    assert result.category is RiskCategory.MINIMAL
    assert codes(result) == ["ai_literacy", "voluntary_codes"]
    assert result.risk_score == 5
    assert result.max_penalty is None


@pytest.mark.parametrize(
    "partial, finding",
    [
        ({"role": "provider", "is_ai_system": False}, "scope.not_ai_system"),
        ({"role": "provider", "is_ai_system": True, "eu_nexus": False}, "scope.no_eu_nexus"),
        ({"role": "deployer", "is_ai_system": True, "eu_nexus": True, "exclusion": "military"}, "scope.excluded.military"),
    ],
)
def test_out_of_scope_ends_questionnaire(partial, finding):
    assert next_question(partial) is None
    result = assess(partial)
    assert result.category is RiskCategory.OUT_OF_SCOPE
    assert result.risk_score == 0
    assert result.obligations == []
    assert [f.code for f in result.findings] == [finding]


def test_prohibited_practice_is_unacceptable_and_ends_questionnaire():
    partial = {
        "role": "provider",
        "is_ai_system": True,
        "eu_nexus": True,
        "exclusion": "none",
        "prohibited_practices": ["social_scoring", "emotion_workplace"],
    }
    assert next_question(partial) is None
    result = assess(partial)
    assert result.category is RiskCategory.UNACCEPTABLE
    assert result.risk_score == 100
    assert {f.code for f in result.findings} == {"prohibited.social_scoring", "prohibited.emotion_workplace"}
    assert "cease_prohibited" in codes(result)
    assert "35 M€" in result.max_penalty


def test_annex_i_product_with_third_party_assessment_is_high_risk_from_2027():
    result = assess(answers(annex_i_product=True, annex_i_third_party=True))
    assert result.category is RiskCategory.HIGH
    assert "hr_conformity_assessment_annex_i" in codes(result)
    assert "hr_conformity_assessment" not in codes(result)
    assert all(o.applies_from == "2 août 2027" for o in result.obligations if o.code.startswith("hr_"))


def test_annex_i_without_third_party_assessment_is_not_high_risk():
    result = assess(answers(annex_i_product=True, annex_i_third_party=False))
    assert result.category is RiskCategory.MINIMAL


def test_annex_iii_with_profiling_is_always_high_risk():
    a = answers(annex_iii_uses=["recruitment"], profiling=True)
    assert next_question(a) is None  # derogation question is skipped
    result = assess(a)
    assert result.category is RiskCategory.HIGH
    assert "high.profiling" in {f.code for f in result.findings}
    assert "hr_technical_documentation" in codes(result)
    assert all(o.applies_from == "2 août 2026" for o in result.obligations if o.code.startswith("hr_"))


def test_annex_iii_without_derogation_is_high_risk():
    result = assess(answers(annex_iii_uses=["credit_scoring"], profiling=False, derogation="none"))
    assert result.category is RiskCategory.HIGH


def test_article_6_3_derogation_requires_documentation_and_registration():
    result = assess(answers(annex_iii_uses=["education_access"], profiling=False, derogation="preparatory"))
    assert result.category is RiskCategory.MINIMAL
    assert {"derogation_documentation", "derogation_registration"} <= set(codes(result))
    assert any("6(3)" in flag for flag in result.flags)


def test_high_risk_deployer_obligations_include_fria():
    result = assess(answers(role="deployer", annex_iii_uses=["credit_scoring"], profiling=True))
    assert codes(result) == ["ai_literacy", "hr_deployer_duties", "hr_fria", "hr_deployer_inform", "hr_right_to_explanation", "hr_value_chain"]


def test_fria_not_required_for_critical_infrastructure_only():
    result = assess(answers(role="deployer", annex_iii_uses=["critical_infrastructure"], profiling=False, derogation="none"))
    assert "hr_fria" not in codes(result)


@pytest.mark.parametrize("role, expected", [("importer", "hr_importer_duties"), ("distributor", "hr_distributor_duties")])
def test_high_risk_importer_and_distributor(role, expected):
    result = assess(answers(role=role, annex_iii_uses=["recruitment"], profiling=True))
    assert expected in codes(result)
    assert "hr_risk_management" not in codes(result)


def test_transparency_obligations_depend_on_role():
    provider = assess(answers(transparency_cases=["direct_interaction", "deepfake"]))
    assert provider.category is RiskCategory.TRANSPARENCY
    assert "tr_direct_interaction" in codes(provider)
    assert "tr_deepfake" not in codes(provider)

    deployer = assess(answers(role="deployer", transparency_cases=["direct_interaction", "deepfake"]))
    assert "tr_deepfake" in codes(deployer)
    assert "tr_direct_interaction" not in codes(deployer)


def test_high_risk_system_keeps_transparency_obligations():
    result = assess(answers(annex_iii_uses=["recruitment"], profiling=True, transparency_cases=["direct_interaction"]))
    assert result.category is RiskCategory.HIGH
    assert "tr_direct_interaction" in codes(result)


def test_gpai_systemic_risk_model():
    result = assess(answers(gpai_model=True, gpai_systemic=True))
    assert {"gpai_provider", "gpai_systemic"} <= set(codes(result))
    assert "Modèle GPAI à risque systémique" in result.flags


def test_gpai_question_only_for_providers():
    a = answers(role="deployer")
    a.pop("gpai_model")
    assert next_question(a) is None
    assert "gpai_provider" not in codes(assess(answers(role="deployer", gpai_model=True)))


def test_context_factors_raise_score_within_band():
    low = assess(answers(annex_iii_uses=["recruitment"], profiling=True))
    high = assess(answers(
        annex_iii_uses=["recruitment"],
        profiling=True,
        human_oversight="automated",
        scale="large",
        vulnerable_groups=True,
        personal_data="sensitive",
    ))
    assert low.risk_score == 60
    assert high.risk_score == 95
    assert sum(f.points for f in high.score_factors) == pytest.approx(95, abs=0.5)


def test_answers_from_abandoned_branch_are_ignored():
    # The user first said the system is a product under Annex I, then changed
    # the answer: the follow-up answer must no longer count.
    result = assess(answers(annex_i_product=False, annex_i_third_party=True))
    assert result.category is RiskCategory.MINIMAL


@pytest.mark.parametrize(
    "bad",
    [
        {"unknown": True},
        {"role": "ceo"},
        {"is_ai_system": "yes"},
        {"prohibited_practices": []},
        {"prohibited_practices": ["none", "social_scoring"]},
        {"annex_iii_uses": ["teleportation"]},
    ],
)
def test_invalid_answers_are_rejected(bad):
    with pytest.raises(ValueError):
        assess(bad)
