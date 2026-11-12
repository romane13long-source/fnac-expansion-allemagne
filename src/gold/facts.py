"""Silver -> Gold (3/3) : fact_population, fact_indicateurs_officiels, fact_magasins_concurrents (README § 2.6)."""
import pandas as pd

from paths import GOLD, SILVER

dims = {name: pd.read_csv(GOLD / f"{name}.csv", dtype=str)
        for name in ["dim_pays", "dim_annee", "dim_indicateur", "dim_commune"]}


def check_fk(table, column, dim, dim_column):
    """Chaque clé étrangère doit exister dans sa dimension (intégrité du modèle en étoile)."""
    unknown = set(table[column].astype(str)) - set(dims[dim][dim_column])
    assert not unknown, f"{column} inconnu(s) dans {dim} : {sorted(unknown)[:5]}"


# fact_population : grain = pays × année
population = pd.read_csv(SILVER / "population.csv").rename(columns={"pays": "pays_id"})
fact_population = population[["pays_id", "annee", "population_1er_janvier", "statut_eurostat"]]
assert not fact_population.duplicated(["pays_id", "annee"]).any()
check_fk(fact_population, "pays_id", "dim_pays", "pays_id")
check_fk(fact_population, "annee", "dim_annee", "annee")

# fact_indicateurs_officiels : grain = indicateur × pays ; pays vide = GROUPE (règle de gestion n° 7)
sources = pd.read_csv(SILVER / "sources_officielles.csv", dtype={"pays": str})
sources["pays"] = sources["pays"].fillna("GROUPE")
fact_indicateurs = (sources.rename(columns={"indicateur": "indicateur_id", "pays": "pays_id"})
                    [["indicateur_id", "pays_id", "annee", "valeur"]])
assert not fact_indicateurs.duplicated(["indicateur_id", "pays_id"]).any()
assert fact_indicateurs["pays_id"].ne("").all(), "une clé n'est jamais vide (règle n° 7)"
check_fk(fact_indicateurs, "indicateur_id", "dim_indicateur", "indicateur_id")
check_fk(fact_indicateurs, "pays_id", "dim_pays", "pays_id")
check_fk(fact_indicateurs, "annee", "dim_annee", "annee")

# fact_magasins_concurrents : grain = un magasin CECONOMY (MediaMarkt ou Saturn, compté une fois, règle n° 5)
magasins = pd.read_csv(SILVER / "magasins_concurrents.csv", dtype={"code_commune": str})
fact_magasins = magasins[["magasin_id", "enseigne", "code_commune", "methode_rattachement"]].assign(nb_magasins=1)
assert fact_magasins["magasin_id"].is_unique, "magasin compté deux fois"
check_fk(fact_magasins, "code_commune", "dim_commune", "code_commune")

for name, table in {"fact_population": fact_population, "fact_indicateurs_officiels": fact_indicateurs,
                    "fact_magasins_concurrents": fact_magasins}.items():
    table.to_csv(GOLD / f"{name}.csv", index=False)
    print(f"{name}.csv : {len(table)} lignes")
print(f"magasins CECONOMY par Land : {len(magasins['land_code'].unique())} Länder couverts sur 16")
