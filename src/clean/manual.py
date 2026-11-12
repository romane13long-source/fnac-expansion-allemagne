"""Manuel -> Silver : contrôle les chiffres relevés à la main et leur donne une année commune."""
import re

import pandas as pd

from paths import MANUAL, SILVER


def to_year(period):
    """Ramène chaque période à une année, pour pouvoir joindre avec Eurostat.

    « 2025-12-31 » -> 2025 ; « 2024/25 » (exercice décalé) -> 2025, année de clôture ;
    « consulté 2026-11-11 » (taux en vigueur) -> 2026.
    """
    years = re.findall(r"\d{4}(?:/\d{2})?", period)
    assert years, f"période illisible : {period!r}"
    year = years[-1]
    return int(year[:2] + year[-2:]) if "/" in year else int(year)


facts = pd.read_csv(MANUAL / "sources_officielles.csv", dtype={"pays": str, "page": str})

# Chaque chiffre doit être un nombre, avec sa source et un lien officiel
facts["valeur"] = pd.to_numeric(facts["valeur"], errors="raise")
assert facts["source"].notna().all(), "chiffre sans source"
assert facts["url"].str.startswith("https://").all(), "lien manquant ou non sécurisé"
assert not facts.duplicated(["indicateur", "pays"]).any(), "même indicateur saisi deux fois"
facts["pays"] = facts["pays"].fillna("")
facts["annee"] = facts["periode"].map(to_year)

facts.to_csv(SILVER / "sources_officielles.csv", index=False)
print(f"sources_officielles.csv : {len(facts)} chiffres, {facts['source'].nunique()} documents sources, "
      f"années {sorted(facts['annee'].unique())}")

# Autres concurrents : comptages nationaux, sans géolocalisation magasin (règle de gestion n° 11)
autres = pd.read_csv(MANUAL / "concurrents_autres.csv", dtype={"pays": str})
autres["nb_points_de_vente"] = pd.to_numeric(autres["nb_points_de_vente"], errors="raise").astype(int)
autres["annee"] = autres["periode"].map(to_year)
assert autres.notna().all().all(), "concurrents_autres : case vide"
assert autres["url"].str.startswith("https://").all(), "concurrents_autres : lien manquant ou non sécurisé"
assert not autres.duplicated(["enseigne", "pays"]).any(), "concurrents_autres : enseigne saisie deux fois"
autres.to_csv(SILVER / "concurrents_autres.csv", index=False)
print(f"concurrents_autres.csv : {len(autres)} enseignes, "
      f"{autres['nb_points_de_vente'].sum()} points de vente (0 = pure player)")

for name in ["hubs_logistiques", "correspondance_categories", "hypotheses_roi"]:
    table = pd.read_csv(MANUAL / f"{name}.csv", dtype=str)
    assert table.notna().all().all(), f"{name} : case vide"
    table.to_csv(SILVER / f"{name}.csv", index=False)
    print(f"{name}.csv : {len(table)} lignes")
