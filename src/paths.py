"""Chemins du projet et constantes partagées."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANUAL = ROOT / "data" / "manual"   # chiffres relevés à la main dans des documents officiels (versionnés)
RAW = ROOT / "data" / "raw"         # Bronze : téléchargements, jamais modifiés
SILVER = ROOT / "data" / "silver"   # Silver : une table propre par source
GOLD = ROOT / "data" / "gold"       # Gold : modèle en étoile + KPI

for folder in (RAW, SILVER, GOLD):
    folder.mkdir(parents=True, exist_ok=True)

COUNTRIES = ["DE", "FR"]
FIRST_YEAR = 2015


def open_url(url, timeout=120):
    """Ouvre une URL en HTTPS avec vérification du certificat (liste d'autorités fournie par certifi)."""
    import ssl
    import urllib.request

    import certifi

    context = ssl.create_default_context(cafile=certifi.where())
    return urllib.request.urlopen(url, timeout=timeout, context=context)
