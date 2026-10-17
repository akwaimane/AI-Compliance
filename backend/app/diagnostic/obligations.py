"""Catalogue of AI Act obligations, mapped to ISO/IEC 42001:2023.

Application dates follow Article 113 of Regulation (EU) 2024/1689 as
originally adopted. They are kept in one place so they can be updated if the
timeline is amended.
"""

from __future__ import annotations

from .models import Obligation

FEB_2025 = "2 février 2025"
AUG_2025 = "2 août 2025"
AUG_2026 = "2 août 2026"
AUG_2027 = "2 août 2027"

# ISO/IEC 42001:2023 clauses and Annex A control objectives.
ISO_POLICIES = "A.2 Politiques relatives à l'IA"
ISO_ORGANIZATION = "A.3 Organisation interne"
ISO_RESOURCES = "A.4 Ressources des systèmes d'IA"
ISO_IMPACT = "A.5 Évaluation des impacts des systèmes d'IA"
ISO_LIFECYCLE = "A.6 Cycle de vie des systèmes d'IA"
ISO_DATA = "A.7 Données pour les systèmes d'IA"
ISO_INFORMATION = "A.8 Informations pour les parties intéressées"
ISO_USE = "A.9 Utilisation des systèmes d'IA"
ISO_THIRD_PARTIES = "A.10 Relations avec les tiers et les clients"
ISO_RISK = "§6.1 Actions face aux risques et opportunités"
ISO_COMPETENCE = "§7.2 Compétences"
ISO_DOCUMENTED_INFO = "§7.5 Informations documentées"
ISO_OPERATION = "§8 Fonctionnement"
ISO_MONITORING = "§9.1 Surveillance, mesure, analyse et évaluation"
ISO_IMPROVEMENT = "§10 Amélioration"


def _o(code: str, title: str, description: str, legal_reference: str, applies_from: str, *iso: str) -> Obligation:
    return Obligation(
        code=code,
        title=title,
        description=description,
        legal_reference=legal_reference,
        applies_from=applies_from,
        iso42001_controls=list(iso),
    )


CATALOG: dict[str, Obligation] = {o.code: o for o in [
    _o("ai_literacy", "Maîtrise de l'IA",
       "Garantir un niveau suffisant de maîtrise de l'IA du personnel et des personnes qui exploitent ou utilisent le système pour le compte de l'organisation.",
       "Art. 4", FEB_2025, ISO_COMPETENCE, ISO_RESOURCES),
    _o("cease_prohibited", "Cessation immédiate de la pratique interdite",
       "Le système ne peut être ni mis sur le marché, ni mis en service, ni utilisé dans l'UE. Retirer ou reconcevoir le système, et documenter la décision.",
       "Art. 5", FEB_2025, ISO_POLICIES, ISO_IMPACT),
    # High-risk: providers
    _o("hr_provider_duties", "Obligations générales du fournisseur",
       "Assurer la conformité aux exigences du chapitre III, section 2 ; indiquer nom et adresse ; conserver la documentation 10 ans ; prendre des mesures correctives.",
       "Art. 16, 18, 20", AUG_2026, ISO_POLICIES, ISO_ORGANIZATION),
    _o("hr_risk_management", "Système de gestion des risques",
       "Processus itératif couvrant tout le cycle de vie : identification, estimation et évaluation des risques pour la santé, la sécurité et les droits fondamentaux, mesures de maîtrise et tests.",
       "Art. 9", AUG_2026, ISO_RISK, ISO_IMPACT, ISO_LIFECYCLE),
    _o("hr_data_governance", "Données et gouvernance des données",
       "Jeux d'entraînement, de validation et de test pertinents, représentatifs et, dans la mesure du possible, exempts d'erreurs ; examen des biais possibles et mesures d'atténuation.",
       "Art. 10", AUG_2026, ISO_DATA),
    _o("hr_technical_documentation", "Documentation technique (annexe IV)",
       "Établir avant la mise sur le marché, et tenir à jour, la documentation technique démontrant la conformité du système.",
       "Art. 11, annexe IV", AUG_2026, ISO_DOCUMENTED_INFO, ISO_LIFECYCLE),
    _o("hr_record_keeping", "Journalisation",
       "Permettre techniquement l'enregistrement automatique des événements (logs) tout au long de la durée de vie du système.",
       "Art. 12, 19", AUG_2026, ISO_LIFECYCLE),
    _o("hr_instructions", "Transparence et notice d'utilisation",
       "Fournir aux déployeurs une notice d'utilisation claire : finalité, niveau d'exactitude, limites, mesures de contrôle humain, durée de vie.",
       "Art. 13", AUG_2026, ISO_INFORMATION),
    _o("hr_human_oversight", "Contrôle humain",
       "Concevoir le système pour qu'il puisse être supervisé efficacement par des personnes physiques, y compris la possibilité de l'interrompre ou d'ignorer ses sorties.",
       "Art. 14", AUG_2026, ISO_LIFECYCLE, ISO_USE),
    _o("hr_accuracy_robustness", "Exactitude, robustesse et cybersécurité",
       "Atteindre un niveau approprié d'exactitude, de robustesse et de cybersécurité, et le maintenir tout au long du cycle de vie.",
       "Art. 15", AUG_2026, ISO_LIFECYCLE),
    _o("hr_qms", "Système de gestion de la qualité",
       "Mettre en place un système de gestion de la qualité documenté (politiques, procédures, instructions). Un SMIA ISO/IEC 42001 en constitue une base solide.",
       "Art. 17", AUG_2026, ISO_POLICIES, ISO_ORGANIZATION, ISO_OPERATION, ISO_IMPROVEMENT),
    _o("hr_conformity_assessment", "Évaluation de la conformité",
       "Suivre la procédure d'évaluation de la conformité applicable (contrôle interne ou organisme notifié) avant la mise sur le marché.",
       "Art. 43", AUG_2026, ISO_OPERATION),
    _o("hr_conformity_assessment_annex_i", "Évaluation de la conformité selon la législation produit",
       "Intégrer les exigences de l'AI Act à l'évaluation de la conformité par un organisme notifié prévue par la législation de l'annexe I.",
       "Art. 43(3)", AUG_2027, ISO_OPERATION),
    _o("hr_declaration_ce", "Déclaration UE de conformité et marquage CE",
       "Rédiger la déclaration UE de conformité et apposer le marquage CE.",
       "Art. 47, 48", AUG_2026, ISO_DOCUMENTED_INFO),
    _o("hr_registration", "Enregistrement dans la base de données de l'UE",
       "Enregistrer le système et le fournisseur dans la base de données de l'UE avant la mise sur le marché.",
       "Art. 49(1), 71", AUG_2026, ISO_DOCUMENTED_INFO),
    _o("hr_post_market", "Surveillance après commercialisation",
       "Établir et documenter un système de surveillance après commercialisation proportionné aux risques.",
       "Art. 72", AUG_2026, ISO_MONITORING, ISO_LIFECYCLE),
    _o("hr_incident_reporting", "Notification des incidents graves",
       "Signaler tout incident grave aux autorités de surveillance du marché dans les délais prescrits (au plus tard 15 jours).",
       "Art. 73", AUG_2026, ISO_IMPROVEMENT, ISO_INFORMATION),
    # High-risk: deployers
    _o("hr_deployer_duties", "Obligations du déployeur",
       "Utiliser le système conformément à la notice ; confier le contrôle humain à des personnes compétentes ; veiller à la pertinence des données d'entrée ; surveiller le fonctionnement ; conserver les logs au moins 6 mois.",
       "Art. 26", AUG_2026, ISO_USE, ISO_RESOURCES),
    _o("hr_deployer_inform", "Information des travailleurs et des personnes concernées",
       "Informer les représentants des travailleurs avant la mise en service sur le lieu de travail, et les personnes faisant l'objet de décisions assistées par le système.",
       "Art. 26(7), 26(11)", AUG_2026, ISO_INFORMATION),
    _o("hr_fria", "Analyse d'impact sur les droits fondamentaux (FRIA)",
       "Obligatoire pour les organismes de droit public, les entités privées fournissant des services publics, et pour les usages de l'annexe III, 5(b) et 5(c). À réaliser avant la première utilisation.",
       "Art. 27", AUG_2026, ISO_IMPACT),
    _o("hr_right_to_explanation", "Droit à l'explication des décisions individuelles",
       "Fournir aux personnes concernées, sur demande, des explications claires sur le rôle du système dans la décision.",
       "Art. 86", AUG_2026, ISO_INFORMATION),
    # High-risk: importers and distributors
    _o("hr_importer_duties", "Obligations de l'importateur",
       "Vérifier avant la mise sur le marché : évaluation de la conformité, documentation technique, marquage CE, déclaration UE de conformité et mandataire désigné.",
       "Art. 23", AUG_2026, ISO_THIRD_PARTIES),
    _o("hr_distributor_duties", "Obligations du distributeur",
       "Vérifier le marquage CE, la déclaration UE de conformité et la notice d'utilisation ; ne pas mettre à disposition un système non conforme.",
       "Art. 24", AUG_2026, ISO_THIRD_PARTIES),
    _o("hr_value_chain", "Requalification en fournisseur",
       "Vous devenez fournisseur si vous apposez votre nom ou marque sur le système, si vous le modifiez substantiellement, ou si vous en changez la destination pour le rendre à haut risque.",
       "Art. 25", AUG_2026, ISO_THIRD_PARTIES),
    # Article 6(3) derogation
    _o("derogation_documentation", "Documentation de l'évaluation de non-haut risque",
       "Documenter, avant la mise sur le marché, l'évaluation concluant que le système ne présente pas de risque important, et la fournir aux autorités sur demande.",
       "Art. 6(4)", AUG_2026, ISO_IMPACT, ISO_DOCUMENTED_INFO),
    _o("derogation_registration", "Enregistrement dans la base de données de l'UE",
       "Enregistrer le système dans la base de données de l'UE même s'il est considéré comme non à haut risque.",
       "Art. 49(2)", AUG_2026, ISO_DOCUMENTED_INFO),
    # Transparency
    _o("tr_direct_interaction", "Information sur l'interaction avec une IA",
       "Concevoir le système pour que les personnes soient informées qu'elles interagissent avec un système d'IA, sauf si c'est évident.",
       "Art. 50(1)", AUG_2026, ISO_INFORMATION),
    _o("tr_synthetic_content", "Marquage des contenus synthétiques",
       "Marquer les sorties audio, image, vidéo ou texte dans un format lisible par machine et détectable comme généré ou manipulé artificiellement.",
       "Art. 50(2)", AUG_2026, ISO_INFORMATION, ISO_LIFECYCLE),
    _o("tr_emotion_biometric", "Information des personnes exposées",
       "Informer les personnes exposées au fonctionnement d'un système de reconnaissance des émotions ou de catégorisation biométrique.",
       "Art. 50(3)", AUG_2026, ISO_INFORMATION),
    _o("tr_deepfake", "Divulgation des hypertrucages",
       "Indiquer que le contenu (image, audio, vidéo) a été généré ou manipulé artificiellement.",
       "Art. 50(4)", AUG_2026, ISO_INFORMATION),
    _o("tr_public_interest_text", "Divulgation des textes d'intérêt public générés",
       "Indiquer que le texte a été généré ou manipulé artificiellement, sauf relecture humaine et responsabilité éditoriale.",
       "Art. 50(4)", AUG_2026, ISO_INFORMATION),
    # General-purpose AI models
    _o("gpai_provider", "Obligations des fournisseurs de modèles GPAI",
       "Documentation technique du modèle, informations pour les fournisseurs en aval, politique de respect du droit d'auteur, résumé public des données d'entraînement.",
       "Art. 53", AUG_2025, ISO_DOCUMENTED_INFO, ISO_DATA, ISO_THIRD_PARTIES),
    _o("gpai_systemic", "Obligations des modèles GPAI à risque systémique",
       "Évaluation du modèle et tests adversariaux, évaluation et atténuation des risques systémiques, notification des incidents graves, cybersécurité adéquate.",
       "Art. 55", AUG_2025, ISO_RISK, ISO_LIFECYCLE, ISO_IMPROVEMENT),
    # Voluntary
    _o("voluntary_codes", "Codes de conduite volontaires",
       "Aucune obligation spécifique au-delà de la maîtrise de l'IA. L'adoption volontaire de codes de conduite et d'un SMIA ISO/IEC 42001 est encouragée.",
       "Art. 95", AUG_2026, ISO_POLICIES),
]}

TRANSPARENCY_OBLIGATIONS: dict[str, tuple[str, set[str]]] = {
    # transparency case -> (obligation code, roles responsible)
    "direct_interaction": ("tr_direct_interaction", {"provider", "importer", "distributor"}),
    "synthetic_content": ("tr_synthetic_content", {"provider", "importer", "distributor"}),
    "emotion_or_biometric": ("tr_emotion_biometric", {"deployer"}),
    "deepfake": ("tr_deepfake", {"deployer"}),
    "public_interest_text": ("tr_public_interest_text", {"deployer"}),
}

HIGH_RISK_PROVIDER = [
    "hr_provider_duties",
    "hr_risk_management",
    "hr_data_governance",
    "hr_technical_documentation",
    "hr_record_keeping",
    "hr_instructions",
    "hr_human_oversight",
    "hr_accuracy_robustness",
    "hr_qms",
    "hr_conformity_assessment",
    "hr_declaration_ce",
    "hr_registration",
    "hr_post_market",
    "hr_incident_reporting",
]

HIGH_RISK_DEPLOYER = ["hr_deployer_duties", "hr_deployer_inform", "hr_right_to_explanation"]
