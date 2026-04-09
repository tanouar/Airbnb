---
title: Documentation du projet
layout: default
nav_order: 1
---

# Documentation technique — Airbnb Analytics France

---

## Table des matières

1. [Mise en place de l'environnement](#mise-en-place-de-lenvironnement)
2. [Structure du dépôt](#structure-du-dépôt)
3. [Étape 1 — Exploration des données (EDA)](#étape-1--exploration-des-données-eda)
4. [Étape 2 — Web Scraping & Base de données SQL](#étape-2--web-scraping--base-de-données-sql)
5. [Étape 3 — Analyse avec DuckDB](#étape-3--analyse-avec-duckdb)
6. [Étape 4 — Supabase](#étape-4--supabase)
7. [Étape 5 — API Données Foncières](#étape-5--api-données-foncières)
8. [Étape 6 — Application Streamlit](#étape-6--application-streamlit)
9. [CI/CD — Pipeline de qualité](#cicd--pipeline-de-qualité)
10. [Conventions de contribution](#conventions-de-contribution)

---

## Mise en place de l'environnement

### Installation des dépendances

```bash
pip install -r requirements.txt
pip install -r requirements-lint.txt
```

> 💡 **Recommandé :** utiliser **Google Colab** pour les notebooks afin de bénéficier de ressources cloud (CPU/RAM) adaptées à la volumétrie des données.

### Variables d'environnement

Créer un fichier `.env` à la racine du projet :

```env
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=votre-clé-api
DVF_API_KEY=votre-clé-api-données-foncières   # si requise
```

---

## Structure du dépôt

```text
Airbnb/
├── notebooks/              # Notebooks d'exploration et d'analyse
│   └── eda.ipynb           # EDA — Dataset Inside Airbnb Paris
├── data/                   # Données brutes et transformées (gitignore)
│   ├── raw/                # Fichiers CSV Inside Airbnb bruts
│   └── processed/          # Données nettoyées et agrégées
├── src/                    # Scripts Python
│   ├── scraping/           # Web scraping Airbnb France
│   ├── etl/                # Transformation et chargement des données
│   └── api/                # Connexion API Données Foncières
├── sql/                    # Requêtes DuckDB et schémas SQL
├── app/                    # Application Streamlit
├── tests/                  # Tests unitaires et d'intégration
├── .github/
│   ├── workflows/          # Pipeline CI/CD GitHub Actions
│   ├── CONTRIBUTING.md     # Guide de contribution
│   ├── COMMIT_CONVENTION.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── ISSUE_TEMPLATE/
├── docs/                   # Documentation technique (ce site)
├── requirements.txt
└── README.md
```

---

## Étape 1 — Exploration des données (EDA)

**Notebook :** [`notebooks/eda.ipynb`](../notebooks/eda.ipynb)

- Téléchargement du dataset Paris depuis [Inside Airbnb](http://insideairbnb.com/get-the-data/)
- Analyse exploratoire : distributions, valeurs manquantes, corrélations
- Visualisations des prix, types de logements, quartiers et taux d'occupation
- Identification des variables clés pour les étapes suivantes

### Données sources

| Fichier | Description |
|---------|-------------|
| `listings.csv` | Détail de chaque annonce (prix, type, localisation…) |
| `reviews.csv` | Avis des voyageurs |
| `calendar.csv` | Disponibilités et prix par date |
| `neighbourhoods.csv` | Contours géographiques des quartiers |

---

## Étape 2 — Web Scraping & Base de données SQL

- Scraping automatisé des listings Airbnb par ville/région
- Nettoyage et normalisation des données collectées
- Peuplement d'une base de données **SQLite** ou **DuckDB** locale

### Schéma relationnel

```text
listings         — id, name, host_id, city, neighbourhood, price, room_type…
reviews          — listing_id, date, reviewer_id, comments…
calendar         — listing_id, date, available, price…
neighbourhoods   — neighbourhood_group, neighbourhood, geometry…
```

---

## Étape 3 — Analyse avec DuckDB

- Requêtes SQL analytiques par ville, quartier et type de bien
- Calcul des KPIs principaux :
  - **Taux d'occupation estimé** = (365 - jours disponibles) / 365
  - **Revenu mensuel moyen** = taux d'occupation × prix/nuit × 30
  - **Prix par nuit médian** par quartier
- Création de tables agrégées optimisées pour la visualisation

```sql
-- Exemple : KPIs par quartier
SELECT
    neighbourhood,
    ROUND(AVG(price), 2)              AS prix_moyen_nuit,
    ROUND(AVG(365 - availability_365) / 365.0, 2) AS taux_occupation
FROM listings
GROUP BY neighbourhood
ORDER BY taux_occupation DESC;
```

---

## Étape 4 — Supabase

- Export des tables agrégées vers **Supabase** (PostgreSQL managé)
- Configuration des rôles et accès sécurisés via le dashboard Supabase
- Exposition via l'API REST Supabase pour alimentation de l'application Streamlit

```python
from supabase import create_client
import os

client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
data = client.table("listings_aggregated").select("*").execute()
```

---

## Étape 5 — API Données Foncières

**Source :** [API Données Foncières — data.gouv.fr](https://www.data.gouv.fr/dataservices/api-donnees-foncieres)  
**Producteur :** Cerema / Direction Générale de l'Aménagement, du Logement et de la Nature (DGALN)

### Données disponibles

| Jeu de données | Accès | Description |
|----------------|-------|-------------|
| **DVF+ open-data** | 🔓 Libre | Transactions immobilières (ventes) depuis 2019 |
| **Indicateurs de territoire** | 🔓 Ouvert | Prix médians par commune depuis 2010 |
| **DV3F** | 🔐 Restreint | Données enrichies de prix du foncier |
| **Fichiers fonciers** | 🔐 Restreint | Parcelles, propriétaires (acteurs publics) |

### Utilisation dans le projet

- Récupération des transactions DVF+ par code commune ou département
- Croisement avec les données Airbnb pour calculer le **rendement locatif potentiel**
- Formule : `rendement = (revenu_annuel_airbnb / prix_achat_median) × 100`

---

## Étape 6 — Application Streamlit

**Répertoire :** `app/`

### Lancement local

```bash
cd app
pip install -r requirements.txt
streamlit run app.py
```

L'application s'ouvre sur `http://localhost:8501`.

### Fonctionnalités

- Carte interactive des biens rentables par ville/quartier
- Filtres : ville, type de bien, budget, rendement cible
- Graphiques comparatifs Airbnb vs marché immobilier
- Score de rentabilité par zone géographique

---

## CI/CD — Pipeline de qualité

Le workflow GitHub Actions (`.github/workflows/ci.yml`) se déclenche à chaque push sur `main`, `features/*` et `fix/*` modifiant des fichiers `.py`, `.ipynb` ou `requirements*.txt`.

### Étapes du pipeline

| # | Étape | Outil |
|---|-------|-------|
| 1 | Checkout du code | `actions/checkout@v4` |
| 2 | Configuration Python 3.13 | `actions/setup-python@v5` |
| 3 | Installation des dépendances | `pip` |
| 4 | **PEP8 — fichiers `.py`** | `pycodestyle` via `check_pep8.py` |
| 5 | **PEP8 — notebooks `.ipynb`** | `nbqa pycodestyle` |
| 6 | Erreurs logiques | `flake8 --select=E9,F63,F7,F82` |
| 7 | Tests unitaires + couverture | `pytest --cov` |
| 8 | Upload rapport de couverture | `actions/upload-artifact@v4` |

### Vérification locale avant push

```bash
# PEP8 sur les fichiers Python
python -m pycodestyle src/ tests/

# PEP8 sur les notebooks
nbqa pycodestyle notebooks/ --max-line-length=79

# Erreurs logiques
flake8 . --select=E9,F63,F7,F82 --exclude=.git,__pycache__,venv

# Tests
pytest tests/ --verbose
```

---

## Conventions de contribution

> Voir le guide complet dans [`.github/CONTRIBUTING.md`](../.github/CONTRIBUTING.md)

### Format des commits (Conventional Commits)

```
<type>(<scope>): <description courte en français>
```

**Types principaux :** `feat`, `fix`, `docs`, `data`, `refactor`, `test`, `ci`, `chore`

**Scopes principaux :** `eda`, `scraping`, `etl`, `dvf`, `duckdb`, `supabase`, `streamlit`, `notebook`, `ci`

```
feat(streamlit): ajouter le filtre par rendement cible
fix(etl): corriger le calcul du taux d'occupation
data(dvf): intégrer les transactions DVF+ pour Lyon
ci(workflows): ajouter la vérification PEP8 sur les notebooks
```

### Règles PEP8 pour les notebooks

- Longueur de ligne max : **79 caractères**
- Vider les sorties des cellules avant de committer
- Vérifier avec `nbqa pycodestyle notebooks/ --max-line-length=79`

### Nommage des branches

| Type | Exemple |
|------|---------|
| Fonctionnalité | `feature/ajout-filtre-ville` |
| Correction | `fix/calcul-rendement` |
| Documentation | `docs/mise-a-jour-etape5` |
| Données | `data/import-dvf-bordeaux` |
| Notebook | `notebook/eda-lyon` |

