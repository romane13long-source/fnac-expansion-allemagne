"""Silver -> Gold (2/2) : fact_marche, grain = pays × année × catégorie (README § 2.6).

Réunit les dépenses des ménages (Eurostat nama_10_cp18) et l'indice de niveau des prix
(Eurostat prc_ppp_ind_1) grâce à la table de correspondance des catégories (règle de gestion n° 8).
"""
import pandas as pd

from paths import GOLD, SILVER

marche = pd.read_csv(SILVER / "marche.csv")
prix = pd.read_csv(SILVER / "prix.csv")
categories = pd.read_csv(GOLD / "dim_categorie.csv")

# Codes Eurostat -> catégorie de l'équipe (TECH, LIVRES)
marche = marche.merge(categories[["categorie_id", "code_marche"]], left_on="categorie_code", right_on="code_marche",
                      how="inner", validate="many_to_one")
prix = prix.merge(categories[["categorie_id", "code_prix"]], left_on="categorie_code", right_on="code_prix",
                  how="inner", validate="many_to_one")

keys = ["pays", "annee", "categorie_id"]
fact = marche[keys + ["depenses_menages_meur", "statut_eurostat"]].merge(
    prix[keys + ["indice_niveau_prix_ue100", "statut_eurostat"]], on=keys, how="outer",
    suffixes=("_marche", "_prix"), validate="one_to_one")


def statut(row):
    """Un seul champ statut (schéma Gold) : on garde chaque avertissement avec sa provenance (règle n° 3)."""
    parts = [f"{source} : {row[f'statut_eurostat_{source}']}" for source in ("marche", "prix")
             if pd.notna(row[f"statut_eurostat_{source}"])]
    return " ; ".join(parts)


fact["statut_eurostat"] = fact.apply(statut, axis=1)
fact = (fact.rename(columns={"pays": "pays_id"})
        [["pays_id", "annee", "categorie_id", "depenses_menages_meur", "indice_niveau_prix_ue100", "statut_eurostat"]]
        .sort_values(["pays_id", "categorie_id", "annee"]))

# Contrôles : clé unique, clés étrangères connues, aucune ligne perdue
assert not fact.duplicated(["pays_id", "annee", "categorie_id"]).any()
assert set(fact["pays_id"]) <= set(pd.read_csv(GOLD / "dim_pays.csv")["pays_id"])
assert set(fact["annee"]) <= set(pd.read_csv(GOLD / "dim_annee.csv")["annee"])
assert len(marche) == fact["depenses_menages_meur"].notna().sum(), "dépenses perdues dans la jointure"
assert len(prix) == fact["indice_niveau_prix_ue100"].notna().sum(), "indices de prix perdus dans la jointure"

fact.to_csv(GOLD / "fact_marche.csv", index=False)
print(f"fact_marche.csv : {len(fact)} lignes ({fact['annee'].min()}-{fact['annee'].max()}), "
      f"dont {fact['indice_niveau_prix_ue100'].notna().sum()} avec un indice de prix (2022-2025)")
