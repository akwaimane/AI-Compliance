"""AI Risk Categorization Engine.

Turns questionnaire answers into an AI Act risk category, an "AI Risk Score"
(0-100), the findings that justify the category and the applicable
obligations. The engine is pure and stateless: nothing is stored.
"""

from __future__ import annotations

from .models import (
    Answers,
    AssessmentResult,
    Finding,
    Obligation,
    RiskCategory,
    ScoreFactor,
)
from .obligations import (
    AUG_2027,
    CATALOG,
    HIGH_RISK_DEPLOYER,
    HIGH_RISK_PROVIDER,
    TRANSPARENCY_OBLIGATIONS,
)
from .questionnaire import (
    NONE,
    applicable_answers,
    is_out_of_scope,
    is_prohibited,
    option_label,
    selected,
    validate_answers,
)

CATEGORY_LABELS = {
    RiskCategory.OUT_OF_SCOPE: "Hors champ d'application",
    RiskCategory.MINIMAL: "Risque minimal",
    RiskCategory.TRANSPARENCY: "Risque limité (transparence)",
    RiskCategory.HIGH: "Haut risque",
    RiskCategory.UNACCEPTABLE: "Risque inacceptable",
}

# Score band (min, max) of each category; context factors place the system
# within its band.
SCORE_BANDS = {
    RiskCategory.OUT_OF_SCOPE: (0, 0),
    RiskCategory.MINIMAL: (5, 29),
    RiskCategory.TRANSPARENCY: (30, 59),
    RiskCategory.HIGH: (60, 95),
    RiskCategory.UNACCEPTABLE: (100, 100),
}

# Context factor weights; the largest weights of each factor sum to 1.
CONTEXT_WEIGHTS: dict[str, dict[str | bool, float]] = {
    "human_oversight": {"in_the_loop": 0.0, "on_the_loop": 0.15, "automated": 0.3},
    "scale": {"small": 0.0, "medium": 0.12, "large": 0.25},
    "vulnerable_groups": {False: 0.0, True: 0.2},
    "personal_data": {NONE: 0.0, "personal": 0.1, "sensitive": 0.25},
}

CONTEXT_LABELS = {
    "human_oversight": "Supervision humaine",
    "scale": "Nombre de personnes affectées",
    "vulnerable_groups": "Personnes vulnérables",
    "personal_data": "Données traitées",
}

PENALTIES = {
    RiskCategory.UNACCEPTABLE: "Jusqu'à 35 M€ ou 7 % du chiffre d'affaires annuel mondial (art. 99(3))",
    RiskCategory.HIGH: "Jusqu'à 15 M€ ou 3 % du chiffre d'affaires annuel mondial (art. 99(4))",
    RiskCategory.TRANSPARENCY: "Jusqu'à 15 M€ ou 3 % du chiffre d'affaires annuel mondial (art. 99(4))",
}

SUMMARIES = {
    RiskCategory.OUT_OF_SCOPE: "Le système ne relève pas du champ d'application de l'AI Act. D'autres réglementations (RGPD, droit de la consommation, législations sectorielles) peuvent néanmoins s'appliquer.",
    RiskCategory.MINIMAL: "Le système présente un risque minimal. Seule l'obligation de maîtrise de l'IA s'applique ; l'adoption volontaire de bonnes pratiques et d'un SMIA ISO/IEC 42001 est recommandée.",
    RiskCategory.TRANSPARENCY: "Le système est soumis à des obligations de transparence : les personnes doivent savoir qu'elles interagissent avec une IA ou que des contenus ont été générés artificiellement.",
    RiskCategory.HIGH: "Le système est à haut risque. Il doit satisfaire à des exigences strictes (gestion des risques, gouvernance des données, documentation technique, contrôle humain…) et faire l'objet d'une évaluation de la conformité avant sa mise sur le marché.",
    RiskCategory.UNACCEPTABLE: "Le système met en œuvre une pratique interdite par l'article 5 de l'AI Act. Il ne peut être ni mis sur le marché, ni mis en service, ni utilisé dans l'UE.",
}


def assess(raw_answers: Answers) -> AssessmentResult:
    validate_answers(raw_answers)
    answers = applicable_answers(raw_answers)
    role = answers.get("role")

    findings: list[Finding] = []
    obligation_codes: list[str] = []
    flags: list[str] = []
    annex_i_only = False

    if is_out_of_scope(answers):
        category = RiskCategory.OUT_OF_SCOPE
        findings.append(_scope_finding(answers))
    elif is_prohibited(answers):
        category = RiskCategory.UNACCEPTABLE
        for practice in selected(answers, "prohibited_practices"):
            findings.append(Finding(
                code=f"prohibited.{practice}",
                title="Pratique interdite",
                detail=option_label("prohibited_practices", practice),
                legal_reference="Art. 5(1)",
            ))
        obligation_codes += ["cease_prohibited", "ai_literacy"]
    else:
        obligation_codes.append("ai_literacy")
        annex_i = answers.get("annex_i_product") is True and answers.get("annex_i_third_party") is True
        annex_iii = selected(answers, "annex_iii_uses")
        derogation = answers.get("derogation", NONE)
        high_via_annex_iii = bool(annex_iii) and (answers.get("profiling") is True or derogation == NONE)

        if annex_i:
            findings.append(Finding(
                code="high.annex_i",
                title="Produit couvert par l'annexe I",
                detail="Le système est un produit, ou un composant de sécurité d'un produit, soumis à une évaluation de la conformité par un tiers.",
                legal_reference="Art. 6(1)",
            ))
        if high_via_annex_iii:
            for use in annex_iii:
                findings.append(Finding(
                    code=f"high.annex_iii.{use}",
                    title="Usage à haut risque (annexe III)",
                    detail=option_label("annex_iii_uses", use),
                    legal_reference="Art. 6(2), annexe III",
                ))
            if answers.get("profiling") is True:
                findings.append(Finding(
                    code="high.profiling",
                    title="Profilage de personnes physiques",
                    detail="Un système de l'annexe III qui effectue un profilage est toujours considéré comme à haut risque ; aucune dérogation n'est possible.",
                    legal_reference="Art. 6(3), dernier alinéa",
                ))
        elif annex_iii:
            findings.append(Finding(
                code=f"derogation.{derogation}",
                title="Dérogation de l'article 6(3) invoquée",
                detail=f"{option_label('derogation', derogation)}. Le système relève de l'annexe III mais n'est pas considéré comme à haut risque, sous réserve d'une évaluation documentée.",
                legal_reference="Art. 6(3)",
            ))
            flags.append("Dérogation art. 6(3) à documenter")
            if role == "provider":
                obligation_codes += ["derogation_documentation", "derogation_registration"]

        if annex_i or high_via_annex_iii:
            category = RiskCategory.HIGH
            annex_i_only = annex_i and not high_via_annex_iii
            obligation_codes += _high_risk_obligations(role, annex_iii if high_via_annex_iii else [], annex_i_only)
        else:
            category = RiskCategory.MINIMAL

        transparency = selected(answers, "transparency_cases")
        for case in transparency:
            findings.append(Finding(
                code=f"transparency.{case}",
                title="Obligation de transparence",
                detail=option_label("transparency_cases", case),
                legal_reference="Art. 50",
            ))
            code, roles = TRANSPARENCY_OBLIGATIONS[case]
            if role in roles:
                obligation_codes.append(code)
        if transparency and category is RiskCategory.MINIMAL:
            category = RiskCategory.TRANSPARENCY

        if answers.get("gpai_model") is True:
            flags.append("Fournisseur de modèle GPAI")
            obligation_codes.append("gpai_provider")
            if answers.get("gpai_systemic") is True:
                flags.append("Modèle GPAI à risque systémique")
                obligation_codes.append("gpai_systemic")

        if category is RiskCategory.MINIMAL:
            obligation_codes.append("voluntary_codes")

        if answers.get("personal_data") == "sensitive":
            flags.append("Traitement de données sensibles (RGPD art. 9) : AIPD probablement requise")
        elif answers.get("personal_data") == "personal":
            flags.append("Traitement de données personnelles : conformité RGPD à vérifier")
        if answers.get("vulnerable_groups") is True:
            flags.append("Personnes vulnérables affectées")

    score, factors = _score(category, answers)
    return AssessmentResult(
        category=category,
        category_label=CATEGORY_LABELS[category],
        risk_score=score,
        score_factors=factors,
        summary=SUMMARIES[category],
        findings=findings,
        obligations=_resolve(obligation_codes, annex_i_only),
        flags=flags,
        max_penalty=PENALTIES.get(category),
    )


def _scope_finding(answers: Answers) -> Finding:
    if answers.get("is_ai_system") is False:
        return Finding(
            code="scope.not_ai_system",
            title="Pas un système d'IA",
            detail="Le système ne répond pas à la définition d'un système d'IA (absence d'inférence autonome).",
            legal_reference="Art. 3(1)",
        )
    if answers.get("eu_nexus") is False:
        return Finding(
            code="scope.no_eu_nexus",
            title="Absence de lien avec l'UE",
            detail="Le système n'est ni mis sur le marché, ni mis en service, ni utilisé dans l'UE.",
            legal_reference="Art. 2(1)",
        )
    exclusion = answers["exclusion"]
    return Finding(
        code=f"scope.excluded.{exclusion}",
        title="Exclusion du champ d'application",
        detail=option_label("exclusion", exclusion),
        legal_reference="Art. 2",
    )


def _high_risk_obligations(role: str | None, annex_iii_uses: list[str], annex_i_only: bool) -> list[str]:
    if role == "provider":
        codes = list(HIGH_RISK_PROVIDER)
        if annex_i_only:
            codes[codes.index("hr_conformity_assessment")] = "hr_conformity_assessment_annex_i"
        return codes
    if role == "deployer":
        codes = list(HIGH_RISK_DEPLOYER)
        # FRIA does not apply to critical infrastructure (Art. 27(1)).
        if any(use != "critical_infrastructure" for use in annex_iii_uses):
            codes.insert(1, "hr_fria")
        return codes + ["hr_value_chain"]
    if role == "importer":
        return ["hr_importer_duties", "hr_value_chain"]
    if role == "distributor":
        return ["hr_distributor_duties", "hr_value_chain"]
    return []


def _resolve(codes: list[str], annex_i_only: bool) -> list[Obligation]:
    seen: set[str] = set()
    obligations: list[Obligation] = []
    for code in codes:
        if code in seen:
            continue
        seen.add(code)
        obligation = CATALOG[code]
        # High-risk systems under Annex I (Art. 6(1)) apply one year later.
        if annex_i_only and code.startswith("hr_"):
            obligation = obligation.model_copy(update={"applies_from": AUG_2027})
        obligations.append(obligation)
    return obligations


def _score(category: RiskCategory, answers: Answers) -> tuple[int, list[ScoreFactor]]:
    low, high = SCORE_BANDS[category]
    factors = [ScoreFactor(label=f"Base : {CATEGORY_LABELS[category]}", points=low)]
    if high == low:
        return low, factors

    width = high - low
    total = 0.0
    for question_id, weights in CONTEXT_WEIGHTS.items():
        weight = weights.get(answers.get(question_id), 0.0)  # type: ignore[arg-type]
        if weight:
            total += weight
            factors.append(ScoreFactor(label=CONTEXT_LABELS[question_id], points=round(weight * width, 1)))
    return round(low + total * width), factors
