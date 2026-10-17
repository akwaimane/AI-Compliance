"""Conditional questionnaire (decision tree) aligned on Regulation (EU) 2024/1689.

The questionnaire is the single source of truth for the diagnostic flow: the
frontend asks the API for the next question given the answers so far, so the
branching logic lives only here.
"""

from __future__ import annotations

from collections.abc import Callable

from .models import AnswerValue, Answers, Option, Question, QuestionType

NONE = "none"

SECTION_SCOPE = "Champ d'application"
SECTION_PROHIBITED = "Pratiques interdites"
SECTION_GPAI = "Modèles d'IA à usage général"
SECTION_HIGH_RISK = "Haut risque"
SECTION_TRANSPARENCY = "Transparence"
SECTION_CONTEXT = "Contexte d'usage"

ROLES = [
    Option(id="provider", label="Fournisseur", help="Développe le système ou le fait développer et le met sur le marché sous son nom (art. 3(3))."),
    Option(id="deployer", label="Déployeur", help="Utilise le système sous sa propre autorité dans un cadre professionnel (art. 3(4))."),
    Option(id="importer", label="Importateur", help="Met sur le marché de l'UE un système portant le nom d'une entité établie hors UE (art. 3(6))."),
    Option(id="distributor", label="Distributeur", help="Met le système à disposition sur le marché de l'UE, autre que le fournisseur ou l'importateur (art. 3(7))."),
]

EXCLUSIONS = [
    Option(id=NONE, label="Aucune de ces situations"),
    Option(id="military", label="Fins exclusivement militaires, de défense ou de sécurité nationale", help="Art. 2(3)."),
    Option(id="research", label="Recherche et développement scientifiques exclusivement", help="Système développé et mis en service à la seule fin de R&D scientifique (art. 2(6))."),
    Option(id="personal", label="Usage personnel non professionnel (personne physique)", help="Art. 2(10) — applicable aux déployeurs."),
]

PROHIBITED_PRACTICES = [
    Option(id="manipulation", label="Techniques subliminales, manipulatrices ou trompeuses", help="Altérant substantiellement le comportement et causant (ou susceptibles de causer) un préjudice important — art. 5(1)(a)."),
    Option(id="vulnerability", label="Exploitation des vulnérabilités", help="Liées à l'âge, au handicap ou à la situation sociale ou économique — art. 5(1)(b)."),
    Option(id="social_scoring", label="Notation sociale", help="Évaluation ou classification de personnes d'après leur comportement social ou leurs caractéristiques personnelles, entraînant un traitement préjudiciable — art. 5(1)(c)."),
    Option(id="crime_prediction", label="Prédiction d'infractions fondée uniquement sur le profilage", help="Évaluation du risque qu'une personne commette une infraction sur la seule base du profilage ou de traits de personnalité — art. 5(1)(d)."),
    Option(id="facial_scraping", label="Moissonnage non ciblé d'images faciales", help="Constitution ou extension de bases de reconnaissance faciale à partir d'internet ou de vidéosurveillance — art. 5(1)(e)."),
    Option(id="emotion_workplace", label="Reconnaissance des émotions au travail ou dans l'enseignement", help="Hors raisons médicales ou de sécurité — art. 5(1)(f)."),
    Option(id="biometric_categorisation", label="Catégorisation biométrique déduisant des attributs sensibles", help="Origine raciale, opinions politiques, appartenance syndicale, convictions religieuses, vie ou orientation sexuelle — art. 5(1)(g)."),
    Option(id="realtime_rbi", label="Identification biométrique à distance en temps réel par les forces de l'ordre", help="Dans des espaces accessibles au public, hors exceptions strictement encadrées — art. 5(1)(h)."),
    Option(id=NONE, label="Aucune de ces pratiques", exclusive=True),
]

ANNEX_III_USES = [
    Option(id="biometric_identification", label="Identification biométrique à distance", help="Hors vérification dont la seule finalité est de confirmer l'identité d'une personne — annexe III, 1(a)."),
    Option(id="biometric_categorisation", label="Catégorisation biométrique selon des attributs sensibles ou protégés", help="Annexe III, 1(b)."),
    Option(id="emotion_recognition", label="Reconnaissance des émotions", help="Annexe III, 1(c)."),
    Option(id="critical_infrastructure", label="Composant de sécurité d'infrastructures critiques", help="Infrastructures numériques critiques, trafic routier, fourniture d'eau, de gaz, de chauffage ou d'électricité — annexe III, 2."),
    Option(id="education_access", label="Éducation : admission, orientation ou affectation", help="Annexe III, 3(a) et 3(c)."),
    Option(id="education_assessment", label="Éducation : évaluation des acquis ou surveillance des examens", help="Annexe III, 3(b) et 3(d)."),
    Option(id="recruitment", label="Emploi : recrutement et sélection", help="Annonces ciblées, tri des candidatures, évaluation des candidats — annexe III, 4(a)."),
    Option(id="worker_management", label="Emploi : gestion des travailleurs", help="Promotion, licenciement, attribution des tâches, suivi et évaluation des performances — annexe III, 4(b)."),
    Option(id="public_benefits", label="Accès aux prestations et services publics essentiels", help="Évaluation de l'éligibilité par ou pour une autorité publique, y compris soins de santé — annexe III, 5(a)."),
    Option(id="credit_scoring", label="Évaluation de la solvabilité ou score de crédit", help="Hors détection de la fraude financière — annexe III, 5(b)."),
    Option(id="insurance_pricing", label="Évaluation des risques et tarification en assurance vie ou santé", help="Annexe III, 5(c)."),
    Option(id="emergency_triage", label="Tri des appels d'urgence et des patients", help="Évaluation des appels, envoi des secours, triage en urgence — annexe III, 5(d)."),
    Option(id="law_enforcement", label="Activités répressives (forces de l'ordre)", help="Risque de victimisation, polygraphes, fiabilité des preuves, risque de récidive, profilage — annexe III, 6."),
    Option(id="migration", label="Migration, asile et contrôle aux frontières", help="Évaluation des risques, examen des demandes, détection de personnes — annexe III, 7."),
    Option(id="justice", label="Administration de la justice et modes alternatifs de règlement des litiges", help="Annexe III, 8(a)."),
    Option(id="elections", label="Influence sur les élections ou le comportement de vote", help="Annexe III, 8(b)."),
    Option(id=NONE, label="Aucun de ces usages", exclusive=True),
]

DEROGATIONS = [
    Option(id=NONE, label="Aucune de ces conditions"),
    Option(id="narrow_procedural", label="Tâche procédurale étroite", help="Ex. : transformer des données non structurées en données structurées — art. 6(3)(a)."),
    Option(id="improve_human_result", label="Amélioration du résultat d'une activité humaine déjà réalisée", help="Art. 6(3)(b)."),
    Option(id="detect_patterns", label="Détection de schémas décisionnels sans remplacer l'évaluation humaine", help="Le système ne remplace ni n'influence l'évaluation humaine sans examen humain approprié — art. 6(3)(c)."),
    Option(id="preparatory", label="Tâche préparatoire à une évaluation", help="Art. 6(3)(d)."),
]

TRANSPARENCY_CASES = [
    Option(id="direct_interaction", label="Interaction directe avec des personnes (chatbot, assistant vocal…)", help="Art. 50(1)."),
    Option(id="synthetic_content", label="Génération de contenus synthétiques (texte, image, audio, vidéo)", help="Marquage lisible par machine — art. 50(2)."),
    Option(id="emotion_or_biometric", label="Reconnaissance des émotions ou catégorisation biométrique", help="Information des personnes exposées — art. 50(3)."),
    Option(id="deepfake", label="Hypertrucage (deepfake)", help="Contenu ressemblant à des personnes, lieux ou événements réels — art. 50(4)."),
    Option(id="public_interest_text", label="Texte publié pour informer le public sur des questions d'intérêt public", help="Art. 50(4)."),
    Option(id=NONE, label="Aucun de ces cas", exclusive=True),
]

HUMAN_OVERSIGHT = [
    Option(id="in_the_loop", label="Une personne valide chaque décision"),
    Option(id="on_the_loop", label="Une personne supervise et peut intervenir"),
    Option(id="automated", label="Décisions entièrement automatisées"),
]

SCALE = [
    Option(id="small", label="Moins de 1 000 personnes"),
    Option(id="medium", label="De 1 000 à 100 000 personnes"),
    Option(id="large", label="Plus de 100 000 personnes"),
]

PERSONAL_DATA = [
    Option(id=NONE, label="Aucune donnée personnelle"),
    Option(id="personal", label="Données personnelles"),
    Option(id="sensitive", label="Données sensibles", help="Santé, biométrie, origine, opinions, orientation sexuelle… (art. 9 RGPD)."),
]


QUESTIONS: list[Question] = [
    Question(
        id="role",
        section=SECTION_SCOPE,
        text="Quel est le rôle de votre organisation vis-à-vis de ce système d'IA ?",
        help="Les obligations de l'AI Act dépendent du rôle de l'opérateur.",
        type=QuestionType.SINGLE_CHOICE,
        options=ROLES,
        legal_reference="Art. 3",
    ),
    Question(
        id="is_ai_system",
        section=SECTION_SCOPE,
        text="Le système déduit-il, à partir des entrées qu'il reçoit, comment générer des sorties (prédictions, contenus, recommandations ou décisions) avec un certain degré d'autonomie ?",
        help="Un logiciel fondé uniquement sur des règles définies par des humains pour exécuter automatiquement des opérations n'est en principe pas un système d'IA.",
        type=QuestionType.BOOLEAN,
        legal_reference="Art. 3(1)",
    ),
    Question(
        id="eu_nexus",
        section=SECTION_SCOPE,
        text="Le système est-il mis sur le marché ou en service dans l'UE, ou ses sorties sont-elles utilisées dans l'UE ?",
        type=QuestionType.BOOLEAN,
        legal_reference="Art. 2(1)",
    ),
    Question(
        id="exclusion",
        section=SECTION_SCOPE,
        text="Le système relève-t-il de l'une des exclusions suivantes ?",
        type=QuestionType.SINGLE_CHOICE,
        options=EXCLUSIONS,
        legal_reference="Art. 2(3), 2(6), 2(10)",
    ),
    Question(
        id="prohibited_practices",
        section=SECTION_PROHIBITED,
        text="Le système met-il en œuvre l'une des pratiques suivantes ?",
        help="Ces pratiques sont interdites dans l'UE depuis le 2 février 2025.",
        type=QuestionType.MULTI_CHOICE,
        options=PROHIBITED_PRACTICES,
        legal_reference="Art. 5",
    ),
    Question(
        id="gpai_model",
        section=SECTION_GPAI,
        text="Votre organisation fournit-elle un modèle d'IA à usage général (GPAI) intégré à ce système ?",
        help="Un modèle entraîné sur de grandes quantités de données, capable d'exécuter un large éventail de tâches distinctes (ex. : grand modèle de langage).",
        type=QuestionType.BOOLEAN,
        legal_reference="Art. 3(63), art. 53",
    ),
    Question(
        id="gpai_systemic",
        section=SECTION_GPAI,
        text="Ce modèle a-t-il été entraîné avec plus de 10²⁵ FLOPs ou désigné par la Commission comme présentant un risque systémique ?",
        type=QuestionType.BOOLEAN,
        legal_reference="Art. 51",
    ),
    Question(
        id="annex_i_product",
        section=SECTION_HIGH_RISK,
        text="Le système est-il un produit, ou le composant de sécurité d'un produit, couvert par la législation d'harmonisation de l'annexe I ?",
        help="Machines, jouets, dispositifs médicaux et de diagnostic in vitro, équipements radio, ascenseurs, équipements sous pression, véhicules, aviation civile…",
        type=QuestionType.BOOLEAN,
        legal_reference="Art. 6(1), annexe I",
    ),
    Question(
        id="annex_i_third_party",
        section=SECTION_HIGH_RISK,
        text="Ce produit doit-il faire l'objet d'une évaluation de la conformité par un tiers (organisme notifié) ?",
        type=QuestionType.BOOLEAN,
        legal_reference="Art. 6(1)(b)",
    ),
    Question(
        id="annex_iii_uses",
        section=SECTION_HIGH_RISK,
        text="Le système est-il destiné à l'un des usages suivants ?",
        type=QuestionType.MULTI_CHOICE,
        options=ANNEX_III_USES,
        legal_reference="Art. 6(2), annexe III",
    ),
    Question(
        id="profiling",
        section=SECTION_HIGH_RISK,
        text="Le système effectue-t-il un profilage de personnes physiques ?",
        help="Traitement automatisé évaluant des aspects personnels : rendement au travail, situation économique, santé, préférences, fiabilité, comportement, localisation… (art. 4(4) RGPD).",
        type=QuestionType.BOOLEAN,
        legal_reference="Art. 6(3), dernier alinéa",
    ),
    Question(
        id="derogation",
        section=SECTION_HIGH_RISK,
        text="Le système remplit-il l'une des conditions suivantes, sans influencer de manière significative le résultat de la prise de décision ?",
        help="Si vous invoquez une dérogation, l'évaluation doit être documentée et le système enregistré dans la base de données de l'UE.",
        type=QuestionType.SINGLE_CHOICE,
        options=DEROGATIONS,
        legal_reference="Art. 6(3)",
    ),
    Question(
        id="transparency_cases",
        section=SECTION_TRANSPARENCY,
        text="Le système relève-t-il de l'un des cas suivants ?",
        type=QuestionType.MULTI_CHOICE,
        options=TRANSPARENCY_CASES,
        legal_reference="Art. 50",
    ),
    Question(
        id="human_oversight",
        section=SECTION_CONTEXT,
        text="Quel est le niveau de supervision humaine des sorties du système ?",
        type=QuestionType.SINGLE_CHOICE,
        options=HUMAN_OVERSIGHT,
        legal_reference="Art. 14",
    ),
    Question(
        id="scale",
        section=SECTION_CONTEXT,
        text="Combien de personnes sont affectées par le système chaque année ?",
        type=QuestionType.SINGLE_CHOICE,
        options=SCALE,
    ),
    Question(
        id="vulnerable_groups",
        section=SECTION_CONTEXT,
        text="Le système affecte-t-il des personnes vulnérables (mineurs, personnes handicapées, personnes en situation de précarité) ?",
        type=QuestionType.BOOLEAN,
        legal_reference="Art. 9(9)",
    ),
    Question(
        id="personal_data",
        section=SECTION_CONTEXT,
        text="Quelles données le système traite-t-il ?",
        type=QuestionType.SINGLE_CHOICE,
        options=PERSONAL_DATA,
        legal_reference="Art. 10, RGPD",
    ),
]

QUESTIONS_BY_ID: dict[str, Question] = {q.id: q for q in QUESTIONS}


def selected(answers: Answers, question_id: str) -> list[str]:
    """Options selected for a multi-choice question, ignoring "none"."""
    value = answers.get(question_id)
    if not isinstance(value, list):
        return []
    return [v for v in value if v != NONE]


def is_out_of_scope(answers: Answers) -> bool:
    return (
        answers.get("is_ai_system") is False
        or answers.get("eu_nexus") is False
        or answers.get("exclusion") not in (None, NONE)
    )


def is_in_scope(answers: Answers) -> bool:
    return (
        answers.get("is_ai_system") is True
        and answers.get("eu_nexus") is True
        and answers.get("exclusion") == NONE
    )


def is_prohibited(answers: Answers) -> bool:
    return bool(selected(answers, "prohibited_practices"))


def _assessing_risk(answers: Answers) -> bool:
    return is_in_scope(answers) and "prohibited_practices" in answers and not is_prohibited(answers)


_APPLIES: dict[str, Callable[[Answers], bool]] = {
    "role": lambda a: True,
    "is_ai_system": lambda a: True,
    "eu_nexus": lambda a: a.get("is_ai_system") is True,
    "exclusion": lambda a: a.get("is_ai_system") is True and a.get("eu_nexus") is True,
    "prohibited_practices": is_in_scope,
    "gpai_model": lambda a: _assessing_risk(a) and a.get("role") == "provider",
    "gpai_systemic": lambda a: _assessing_risk(a) and a.get("gpai_model") is True,
    "annex_i_product": _assessing_risk,
    "annex_i_third_party": lambda a: _assessing_risk(a) and a.get("annex_i_product") is True,
    "annex_iii_uses": _assessing_risk,
    "profiling": lambda a: _assessing_risk(a) and bool(selected(a, "annex_iii_uses")),
    "derogation": lambda a: _assessing_risk(a) and a.get("profiling") is False,
    "transparency_cases": _assessing_risk,
    "human_oversight": _assessing_risk,
    "scale": _assessing_risk,
    "vulnerable_groups": _assessing_risk,
    "personal_data": _assessing_risk,
}

assert set(_APPLIES) == set(QUESTIONS_BY_ID), "every question needs an applicability rule"


def applies(question_id: str, answers: Answers) -> bool:
    return _APPLIES[question_id](answers)


def is_terminal(answers: Answers) -> bool:
    return is_out_of_scope(answers) or is_prohibited(answers)


def applicable_answers(answers: Answers) -> Answers:
    """Keep only the answers to questions reachable from the other answers.

    Answers left over from a branch the user backed out of are dropped so
    they cannot influence the classification.
    """
    kept: Answers = {}
    for question in QUESTIONS:
        if is_terminal(kept):
            break
        if question.id in answers and applies(question.id, kept):
            kept[question.id] = answers[question.id]
    return kept


def next_question(answers: Answers) -> Question | None:
    answers = applicable_answers(answers)
    if is_terminal(answers):
        return None
    for question in QUESTIONS:
        if question.id not in answers and applies(question.id, answers):
            return question
    return None


# Questions asked on every in-scope path; used to estimate progress before
# the branch is known.
_BASE_PATH = [
    "role", "is_ai_system", "eu_nexus", "exclusion", "prohibited_practices",
    "annex_i_product", "annex_iii_uses", "transparency_cases",
    "human_oversight", "scale", "vulnerable_groups", "personal_data",
]


def progress(answers: Answers) -> tuple[int, float]:
    """Number of applicable answers and estimated completion ratio."""
    answers = applicable_answers(answers)
    answered = len(answers)
    if next_question(answers) is None:
        return answered, 1.0
    remaining = {q for q in _BASE_PATH if q not in answers}
    remaining |= {q.id for q in QUESTIONS if q.id not in answers and applies(q.id, answers)}
    return answered, round(answered / (answered + len(remaining)), 2)


def validate_answer(question: Question, value: AnswerValue) -> None:
    option_ids = {o.id for o in question.options}
    if question.type is QuestionType.BOOLEAN:
        if not isinstance(value, bool):
            raise ValueError(f"'{question.id}' attend une réponse oui/non.")
    elif question.type is QuestionType.SINGLE_CHOICE:
        if not isinstance(value, str) or value not in option_ids:
            raise ValueError(f"'{question.id}' attend l'une des options : {sorted(option_ids)}.")
    else:
        if not isinstance(value, list) or not value:
            raise ValueError(f"'{question.id}' attend une liste non vide d'options.")
        unknown = set(value) - option_ids
        if unknown:
            raise ValueError(f"Options inconnues pour '{question.id}' : {sorted(unknown)}.")
        exclusive = {o.id for o in question.options if o.exclusive}
        if len(value) > 1 and exclusive & set(value):
            raise ValueError(f"'{question.id}' : l'option « aucun » ne peut pas être combinée à d'autres options.")


def validate_answers(answers: Answers) -> None:
    for question_id, value in answers.items():
        question = QUESTIONS_BY_ID.get(question_id)
        if question is None:
            raise ValueError(f"Question inconnue : '{question_id}'.")
        validate_answer(question, value)


def option_label(question_id: str, option_id: str) -> str:
    for option in QUESTIONS_BY_ID[question_id].options:
        if option.id == option_id:
            return option.label
    return option_id
