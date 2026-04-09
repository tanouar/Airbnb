---
title: Accueil
layout: default
nav_order: 0
---

# Airbnb Analytics France — Documentation

Bienvenue sur la documentation du projet **Airbnb Analytics France**, un outil d'analyse et d'aide à la décision pour la sélection de biens immobiliers à fort potentiel locatif court terme.

## Pages disponibles

| Page | Description |
|------|-------------|
| [Documentation](documentation) | Mise en place de l'environnement, pipeline ETL, conventions CI/CD |
| [Workflows CI/CD](workflow) | Détail des GitHub Actions : PEP8, tests, résolution d'erreurs |

## Architecture du projet

```text
Airbnb/
├── notebooks/              # Notebooks d'exploration et d'analyse
│   └── eda.ipynb           # EDA — Dataset Inside Airbnb Paris
├── data/                   # Données brutes et transformées (gitignore)
├── src/                    # Scripts Python (scraping, ETL, API)
│   ├── scraping/           # Web scraping Airbnb France
│   ├── etl/                # Transformation et chargement des données
│   └── api/                # Connexion API Données Foncières
├── sql/                    # Requêtes DuckDB et schémas SQL
├── app/                    # Application Streamlit
├── tests/                  # Tests unitaires et d'intégration
├── .github/workflows/      # Pipeline CI/CD GitHub Actions
├── docs/                   # Documentation technique (ce site)
├── requirements.txt        # Dépendances Python
└── README.md               # Description du projet
```

## Sources de données

| Source | Description |
|--------|-------------|
| [Inside Airbnb](http://insideairbnb.com/get-the-data/) | Listings Airbnb open data pour la France |
| [API Données Foncières](https://www.data.gouv.fr/dataservices/api-donnees-foncieres) | Transactions DVF+ et indicateurs de prix immobiliers (Cerema / DGALN) |
| [Supabase](https://supabase.com/) | Hébergement PostgreSQL managé et API REST |

## Auteur

- **Tarik ANOUAR** — [LinkedIn](https://www.linkedin.com/in/anouartarik)
- **Melanie GORISSE** — [LinkedIn](https://www.linkedin.com/in/m%C3%A9lanie-gorisse/)

