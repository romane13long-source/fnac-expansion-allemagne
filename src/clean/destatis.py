"""Bronze -> Silver : extrait les communes allemandes (population, superficie, coordonnées) du fichier Destatis."""
import pandas as pd

from paths import RAW, SILVER

# Dans le fichier, la colonne « Satzart » donne le niveau de chaque ligne : 10 = Land, 60 = commune
LAND, COMMUNE = "10", "60"

raw = pd.read_excel(RAW / "destatis_gemeinden_31122025.xlsx", sheet_name=1, header=None, skiprows=6, dtype=str)
raw = raw.iloc[:, [0, 2, 3, 4, 5, 6, 7, 8, 9, 14, 15]]
raw.columns = ["satzart", "land", "rb", "kreis", "vb", "gem", "nom", "superficie_km2", "population",
               "longitude", "latitude"]

lands = raw[raw["satzart"] == LAND].set_index("land")["nom"]
communes = raw[raw["satzart"] == COMMUNE].copy()

# Code officiel de la commune (AGS) = Land + district administratif + arrondissement + commune
communes["code_commune"] = communes["land"] + communes["rb"] + communes["kreis"] + communes["gem"]
communes["land_nom"] = communes["land"].map(lands)
# Les coordonnées sont écrites avec une virgule décimale (« 9,43751 ») : conversion en nombre
for col in ["longitude", "latitude"]:
    communes[col] = pd.to_numeric(communes[col].str.replace(",", ".", regex=False))
communes["superficie_km2"] = pd.to_numeric(communes["superficie_km2"])
communes["population"] = pd.to_numeric(communes["population"]).astype(int)

# Destatis liste aussi des zones sans habitants (eaux côtières, territoire fluvial partagé avec le Luxembourg) :
# on ne peut pas y ouvrir de magasin, et leurs coordonnées sont vides ou à 0
uninhabited = communes["population"] == 0
print(f"{uninhabited.sum()} zones sans habitants retirées (forêts, lacs, eaux côtières...), "
      f"ex. : {', '.join(communes.loc[uninhabited, 'nom'].head(3))}")
communes = communes[~uninhabited]

silver = communes[["code_commune", "nom", "land", "land_nom", "population", "superficie_km2",
                   "longitude", "latitude"]].rename(columns={"land": "land_code"})

# Contrôles
assert silver["code_commune"].is_unique, "code commune en double"
assert silver["land_nom"].notna().all(), "commune sans Land"
assert silver["longitude"].between(5.8, 15.1).all() and silver["latitude"].between(47.2, 55.1).all(), \
    "coordonnée hors d'Allemagne"
assert 80e6 < silver["population"].sum() < 86e6, "population totale incohérente"

silver.to_csv(SILVER / "communes.csv", index=False)
big = silver[silver["population"] >= 100_000]
print(f"communes.csv : {len(silver):,} communes, {silver['population'].sum():,} habitants, "
      f"{len(big)} villes de 100 000 habitants ou plus")
