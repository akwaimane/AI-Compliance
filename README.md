# AI-Compliance

Plateforme intégrée de conformité IA : **AI Act (Règlement UE 2024/1689)** & **ISO/IEC 42001 (SMIA)**.

Cette nouvelle version intègre la norme internationale ISO/IEC 42001 (Système de Management de l'IA) en tant que deuxième pilier structurel. La plateforme ne se contente plus d'auditer les risques légaux de l'AI Act : elle fournit l'infrastructure organisationnelle, les politiques et les contrôles exigés pour obtenir la certification ISO 42001.

## État d'avancement (roadmap 5 mois)

| Phase | Livrables | Statut |
|---|---|---|
| Mois 1 : MVP Diagnostic | Arbre décisionnel de risque, moteur de rapport PDF, interface Freemium | ✅ Livré |
| Mois 2 : Engine d'Audit Data | Upload de datasets, métriques de biais (Fairlearn), SHAP | À venir |
| Mois 3 : Pilier ISO 42001 | Politique d'IA, registre des parties prenantes, contrôles de l'annexe A | À venir |
| Mois 4 : Dossier technique & CAPA | Générateur annexe IV, actions correctives, espace auditeur | À venir |
| Mois 5 : SaaS & Scaling | Dashboard unifié, détection de drift, Stripe B2B | À venir |

## Module 1 : Diagnostic Flash (AI Risk Categorization Engine)

Un questionnaire conditionnel de 17 questions classe un système d'IA dans l'une des catégories de l'AI Act :

1. **Champ d'application** : définition d'un système d'IA (art. 3(1)), lien avec l'UE (art. 2(1)), exclusions (art. 2).
2. **Pratiques interdites** (art. 5) → *risque inacceptable*.
3. **Modèles GPAI** (art. 51, 53, 55) pour les fournisseurs.
4. **Haut risque** : produits de l'annexe I (art. 6(1)), usages de l'annexe III (art. 6(2)), profilage et dérogations (art. 6(3)).
5. **Transparence** (art. 50) → *risque limité*.
6. **Contexte** (supervision humaine, échelle, personnes vulnérables, données) : positionne l'**AI Risk Score** (0–100) dans la bande de la catégorie.

Le résultat comprend les constats et leur base légale, les obligations selon le rôle (fournisseur, déployeur, importateur, distributeur) avec leur date d'application et leur **correspondance avec les clauses et contrôles de l'annexe A d'ISO/IEC 42001**, la sanction maximale encourue, et un **rapport PDF** téléchargeable.

L'API est sans état (**Zero-Data Retention**) : les réponses accompagnent chaque requête et rien n'est stocké.

> Les dates d'application suivent l'article 113 du règlement tel qu'adopté et sont centralisées dans `backend/app/diagnostic/obligations.py`. Vérifiez-les si le calendrier est modifié par un acte ultérieur.

## Architecture

```
backend/    API Python FastAPI (sert aussi le frontend en production)
  app/diagnostic/questionnaire.py   Questions et logique conditionnelle (source unique du flux)
  app/diagnostic/engine.py          Classification, score et obligations
  app/diagnostic/obligations.py     Catalogue des obligations ↔ ISO/IEC 42001
  app/reports/pdf.py                Rapport PDF (ReportLab)
  app/api/diagnostic.py             Endpoints REST
frontend/   Next.js 16, TypeScript, Tailwind CSS (export statique)
Dockerfile  Image unique : build du frontend + API FastAPI
render.yaml Déploiement Render (Blueprint)
```

### Endpoints

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/api/v1/diagnostic/questionnaire` | Liste complète des questions |
| `POST` | `/api/v1/diagnostic/next` | Prochaine question selon les réponses `{answers}` |
| `POST` | `/api/v1/diagnostic/assess` | Classification `{profile, answers}` |
| `POST` | `/api/v1/diagnostic/report` | Rapport PDF `{profile, answers}` |

Documentation interactive : http://localhost:8000/docs

## Déploiement sur Render

Toutes les pages sont statiques : le frontend est exporté puis servi par FastAPI, ce qui donne **un seul service** (même origine, pas de CORS, aucune variable à configurer).

1. Donner à Render l'accès au dépôt `ai-compliance` (GitHub → Settings → Applications → Render → Configure).
2. Dans Render : **New → Blueprint**, choisir le dépôt et la branche ; Render lit `render.yaml`.
3. Une fois le déploiement terminé, l'application est disponible sur `https://<nom-du-service>.onrender.com`.

## Démarrage

Avec Docker (même image qu'en production) :

```bash
docker compose up --build                     # http://localhost:8000
```

En local :

```bash
# Backend
cd backend
python -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/uvicorn app.main:app --reload       # http://localhost:8000
.venv/bin/pytest

# Frontend
cd frontend
cp .env.example .env.local
npm install
npm run dev                                   # http://localhost:3000
```

Variables d'environnement : `CORS_ORIGINS` (backend, origines séparées par des virgules) et `NEXT_PUBLIC_API_URL` (frontend).
