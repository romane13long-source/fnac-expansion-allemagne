"""Manuel -> Silver : contrôle les chiffres relevés à la main avant de les utiliser."""
import pandas as pd

from paths import MANUAL, SILVER

facts = pd.read_csv(MANUAL / "sources_officielles.csv", dtype={"pays": str, "page": str})

# Chaque chiffre doit être un nombre, avec sa source et un lien officiel
facts["valeur"] = pd.to_numeric(facts["valeur"], errors="raise")
assert facts["source"].notna().all(), "chiffre sans source"
assert facts["url"].str.startswith("https://").all(), "lien manquant ou non sécurisé"
assert not facts.duplicated(["indicateur", "pays"]).any(), "même indicateur saisi deux fois"
facts["pays"] = facts["pays"].fillna("")

facts.to_csv(SILVER / "sources_officielles.csv", index=False)
print(f"sources_officielles.csv : {len(facts)} chiffres, {facts['source'].nunique()} documents sources")
