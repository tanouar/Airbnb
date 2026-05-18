import json
import logging
import sys
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

# ─── Configuration du logger ────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("pipeline.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("airbnb_pipeline")

# ─── Constantes ─────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CITIES_FILE = BASE_DIR / "cities.json"
INSIDE_AIRBNB_URL = "http://insideairbnb.com/get-the-data/"


# ─── Chargement des villes ───────────────────────────────────────────────────


def load_cities(path: Path) -> list[dict]:
    """Charge la liste des villes depuis le fichier JSON."""
    logger.info("Chargement des villes depuis %s", path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        villes = data.get("villes", [])
        if not villes:
            raise ValueError("La liste 'villes' est vide dans le fichier JSON.")
        logger.info("%d ville(s) chargée(s) : %s", len(villes), [v["nom"] for v in villes])
        return villes
    except FileNotFoundError:
        logger.error("Fichier de villes introuvable : %s", path)
        raise
    except json.JSONDecodeError as e:
        logger.error("Erreur de décodage JSON : %s", e)
        raise


# ─── Scraping des URLs ───────────────────────────────────────────────────────


def fetch_download_urls(page_url: str, city_slugs: list[str]) -> dict[str, str]:
    """
    Récupère les URLs de téléchargement des fichiers listings.csv
    pour les villes françaises spécifiées.

    Utilise pandas.read_html pour valider la présence des tableaux de données,
    et BeautifulSoup pour extraire les liens de téléchargement.
    """
    logger.info("Récupération de la page : %s", page_url)
    try:
        response = requests.get(page_url, timeout=30)
        response.raise_for_status()
    except requests.Timeout:
        logger.error("Délai d'attente dépassé lors de la connexion à %s", page_url)
        raise
    except requests.HTTPError as e:
        logger.error("Erreur HTTP %s lors de la récupération de la page", e.response.status_code)
        raise
    except requests.RequestException as e:
        logger.error("Erreur réseau : %s", e)
        raise

    html = response.text

    # Pandas : validation du nombre de tableaux présents sur la page
    try:
        tables = pd.read_html(html)
        logger.info("%d tableau(x) détecté(s) sur la page via pandas", len(tables))
    except ValueError:
        logger.warning("Aucun tableau parsable par pandas — la structure de la page a peut-être changé.")

    # BeautifulSoup : extraction des liens href
    soup = BeautifulSoup(html, "lxml")
    all_links = [a["href"] for a in soup.find_all("a", href=True)]

    urls: dict[str, str] = {}
    for slug in city_slugs:
        for href in all_links:
            if (
                "/france/" in href
                and f"/{slug}/" in href
                and href.endswith("listings.csv")
            ):
                urls[slug] = href
                logger.info("URL trouvée pour '%-15s : %s", slug + "'", href)
                break
        if slug not in urls:
            logger.warning("Aucune URL trouvée pour la ville : '%s'", slug)

    return urls


# ─── Téléchargement des fichiers CSV ────────────────────────────────────────


def download_csv(url: str, dest_path: Path) -> None:
    """Télécharge un fichier CSV depuis l'URL vers le chemin de destination."""
    logger.info("Téléchargement : %s", url)
    try:
        response = requests.get(url, timeout=120, stream=True)
        response.raise_for_status()
    except requests.Timeout:
        logger.error("Délai d'attente dépassé pour %s", url)
        raise
    except requests.HTTPError as e:
        logger.error("Erreur HTTP %s pour %s", e.response.status_code, url)
        raise
    except requests.RequestException as e:
        logger.error("Erreur réseau lors du téléchargement : %s", e)
        raise

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info("Fichier sauvegardé : %s", dest_path)
    except OSError as e:
        logger.error("Impossible d'écrire le fichier %s : %s", dest_path, e)
        raise


# ─── Pipeline principal ──────────────────────────────────────────────────────


def run_pipeline() -> None:
    logger.info("=== Démarrage du pipeline Airbnb ===")

    # 1. Chargement des villes depuis cities.json
    villes = load_cities(CITIES_FILE)
    slugs = [v["slug"] for v in villes]

    # 2. Scraping des URLs sur Inside Airbnb
    try:
        urls = fetch_download_urls(INSIDE_AIRBNB_URL, slugs)
    except Exception as e:
        logger.critical("Impossible de récupérer les URLs : %s. Arrêt du pipeline.", e)
        return

    if not urls:
        logger.error("Aucune URL trouvée pour les villes demandées. Arrêt du pipeline.")
        return

    # 3. Téléchargement des fichiers CSV dans data/<slug>/listings.csv
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    success, failures = 0, 0

    for ville in villes:
        slug = ville["slug"]
        nom = ville["nom"]

        if slug not in urls:
            logger.warning("Ville ignorée (pas d'URL disponible) : %s", nom)
            failures += 1
            continue

        dest = DATA_DIR / slug / "listings.csv"
        try:
            download_csv(urls[slug], dest)
            success += 1
        except Exception:
            logger.error("Échec du téléchargement pour '%s'. Passage à la suite.", nom)
            failures += 1

    logger.info(
        "=== Pipeline terminé — %d succès, %d échec(s) ===",
        success,
        failures,
    )


# ─── Traitement des données ──────────────────────────────────────────────────
# TODO : section réservée au traitement des données (à compléter par la collègue)
#
# Exemple de signature attendue :
#
# def process_data(df: pd.DataFrame) -> pd.DataFrame:
#     """
#     Nettoie et transforme le DataFrame listings d'une ville.
#
#     Paramètres
#     ----------
#     df : pd.DataFrame
#         Données brutes issues du fichier listings.csv.
#
#     Retourne
#     --------
#     pd.DataFrame
#         Données nettoyées et enrichies.
#     """
#     ...
#     return df


# ─── Point d'entrée ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_pipeline()
