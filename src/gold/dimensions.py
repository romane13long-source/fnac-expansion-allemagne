"""Silver -> Gold (1/2) : les dimensions du modèle en étoile (README § 2.2 et § 2.6)."""
import math

import pandas as pd

from paths import GOLD, SILVER

LAST_YEAR = 2026  # dim_annee couvre 2015 -> 2026 (README § 2.2)


def haversine_km(lon1, lat1, lon2, lat2):
    """Distance à vol d'oiseau entre deux points (en km), rayon moyen de la Terre = 6 371 km."""
    lon1, lat1, lon2, lat2 = map(math.radians, (lon1, lat1, lon2, lat2))
    a = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(a))


marche = pd.read_csv(SILVER / "marche.csv")
prix = pd.read_csv(SILVER / "prix.csv")
population = pd.read_csv(SILVER / "population.csv")
communes = pd.read_csv(SILVER / "communes.csv", dtype={"code_commune": str, "land_code": str})
hubs = pd.read_csv(SILVER / "hubs_logistiques.csv")
categories = pd.read_csv(SILVER / "correspondance_categories.csv")
sources = pd.read_csv(SILVER / "sources_officielles.csv", dtype={"page": str})

# dim_pays : GROUPE pour les chiffres publiés au niveau d'un groupe entier (règle de gestion n° 7)
dim_pays = pd.DataFrame({"pays_id": ["DE", "FR", "GROUPE"],
                         "nom_pays": ["Allemagne", "France", "Groupe (tous pays)"]})

# dim_annee : une année est « provisoire » si au moins une valeur Eurostat de cette année l'est (règle n° 3)
eurostat = pd.concat([marche[["annee", "statut_eurostat"]], prix[["annee", "statut_eurostat"]],
                      population[["annee", "statut_eurostat"]]])
annees_provisoires = set(eurostat.loc[eurostat["statut_eurostat"].eq("provisoire"), "annee"])
min_year = int(eurostat["annee"].min())
dim_annee = pd.DataFrame({"annee": range(min_year, LAST_YEAR + 1)})
dim_annee["est_provisoire"] = dim_annee["annee"].isin(annees_provisoires)

# dim_categorie : la table de correspondance de l'équipe (règle n° 8)
dim_categorie = categories.rename(columns={"code_marche_eurostat": "code_marche", "code_prix_eurostat": "code_prix"})

# dim_land (flocon) puis dim_commune, avec la distance au hub logistique
dim_land = communes[["land_code", "land_nom"]].drop_duplicates().sort_values("land_code")
assert len(hubs) == 1, "un seul hub attendu (Chilly-Mazarin) : la distance devient ambiguë sinon"
hub = hubs.iloc[0]
dim_commune = communes[["code_commune", "nom", "population", "superficie_km2", "longitude", "latitude", "land_code"]].copy()
dim_commune["distance_hub_km"] = [round(haversine_km(hub["longitude"], hub["latitude"], lon, lat), 1)
                                  for lon, lat in zip(dim_commune["longitude"], dim_commune["latitude"])]

# dim_indicateur : un indicateur = une unité et une source (vérifié ci-dessous)
dim_indicateur = (sources[["indicateur", "unite", "source", "page", "url"]]
                  .rename(columns={"indicateur": "indicateur_id"}).drop_duplicates())
assert dim_indicateur["indicateur_id"].is_unique, "un indicateur a deux unités ou deux sources"

# Contrôles d'intégrité
assert dim_commune["code_commune"].is_unique and dim_land["land_code"].is_unique
assert len(dim_land) == 16, f"{len(dim_land)} Länder au lieu de 16"
assert dim_commune["distance_hub_km"].between(200, 1500).all(), "distance hub -> commune hors de l'Allemagne"

tables = {"dim_pays": dim_pays, "dim_annee": dim_annee, "dim_categorie": dim_categorie,
          "dim_land": dim_land, "dim_commune": dim_commune, "dim_indicateur": dim_indicateur}
for name, table in tables.items():
    table.to_csv(GOLD / f"{name}.csv", index=False)
    print(f"{name}.csv : {len(table)} lignes")
print(f"distance au hub : de {dim_commune['distance_hub_km'].min()} à {dim_commune['distance_hub_km'].max()} km")
