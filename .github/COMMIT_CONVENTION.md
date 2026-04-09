# Convention de commits — Conventional Commits

Ce projet suit le standard **[Conventional Commits 1.0.0](https://www.conventionalcommits.org/fr/)**.

---

## Format

```
<type>(<scope>): <description>

[corps optionnel]

[footer optionnel]
```

- **type** : obligatoire — catégorie de la modification
- **scope** : optionnel — composant concerné entre parenthèses
- **description** : obligatoire — résumé en minuscules, sans point final, max 72 caractères
- **corps** : optionnel — contexte supplémentaire (séparé par une ligne vide)
- **footer** : optionnel — références à des issues (`Closes #12`, `Fixes #8`)

---

## Types autorisés

| Type | Usage |
|---|---|
| `feat` | Nouvelle fonctionnalité visible par l'utilisateur |
| `fix` | Correction d'un bug |
| `docs` | Modification de la documentation uniquement |
| `style` | Formatage, espaces, virgules — sans changement logique |
| `refactor` | Restructuration du code sans ajout de fonctionnalité ni correction de bug |
| `perf` | Amélioration des performances |
| `test` | Ajout ou correction de tests |
| `chore` | Maintenance : dépendances, configuration, scripts |
| `data` | Modification des données, pipelines, fichiers CSV/SQL |
| `ci` | Configuration des workflows CI/CD |
| `revert` | Annulation d'un commit précédent |

---

## Scopes suggérés

| Scope | Composant |
|---|---|
| `eda` | Notebook d'exploration (`notebooks/eda.ipynb`) |
| `scraping` | Scripts de web scraping (`src/scraping/`) |
| `etl` | Transformation et chargement des données (`src/etl/`) |
| `dvf` | Intégration API Données Foncières (`src/api/`) |
| `duckdb` | Requêtes et tables DuckDB/SQL (`sql/`) |
| `supabase` | Export et déploiement Supabase |
| `streamlit` | Application Streamlit (`app/`) |
| `notebook` | Notebooks Jupyter |
| `deps` | Dépendances (`requirements.txt`) |
| `ci` | Pipeline CI/CD (`.github/workflows/`) |
| `readme` | Fichier README |
| `docs` | Documentation technique (`docs/`) |

---

## Exemples

```
feat(streamlit): ajouter le filtre par ville et rendement cible

fix(etl): corriger le calcul du taux d'occupation par ville

docs(readme): mettre à jour la description de l'étape 5

data(dvf): intégrer les transactions DVF+ pour Paris et Lyon

refactor(etl): extraire la normalisation dans un module séparé

perf(duckdb): ajouter un index sur la colonne city dans listings

chore(deps): mettre à jour duckdb vers 1.2.0

test(scraping): ajouter les tests unitaires du parser Airbnb

ci(workflows): ajouter la vérification PEP8 sur les notebooks
```

---

## Commits avec breaking change

Ajouter un `!` après le type/scope et un footer `BREAKING CHANGE:` :

```
feat(etl)!: modifier le format de sortie du pipeline de scraping

BREAKING CHANGE: load_listings() retourne désormais un DataFrame
avec un index multi-niveaux (city, neighbourhood) au lieu d'un index simple.
```

---

## Référencer des issues

```
fix(scraping): corriger le timeout lors du scraping de Marseille

Closes #14
```

---

## Règles à respecter

- Toujours en **minuscules**
- Pas de point `.` en fin de description
- Description en **français**
- Un commit = une modification logique (ne pas mélanger fix et feat)
- Eviter les commits vagues : ~~`fix stuff`~~, ~~`wip`~~, ~~`update`~~
