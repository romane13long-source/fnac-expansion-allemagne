"""Gold -> kpi.csv : calcule les KPI du guide du prof (slide 7) à partir du modèle en étoile.

Format long, une ligne = une valeur de KPI. Le dashboard et la brique IA lisent ce fichier.
`nature` dit d'où vient la valeur (règle de gestion n° 10) : mesuré / estimation / hypothèse.
KPI 6 « % du catalogue éligible » (simulé) et le ROI de synthèse ne sont pas calculés ici.
"""
import math

import pandas as pd

from paths import GOLD, SILVER

marche = pd.read_csv(GOLD / "fact_marche.csv")
population = pd.read_csv(GOLD / "fact_population.csv")
ind = pd.read_csv(GOLD / "fact_indicateurs_officiels.csv")
magasins = pd.read_csv(GOLD / "fact_magasins_concurrents.csv", dtype={"code_commune": str})
communes = pd.read_csv(GOLD / "dim_commune.csv", dtype={"code_commune": str, "land_code": str})
lands = pd.read_csv(GOLD / "dim_land.csv", dtype={"land_code": str})


def v(indicateur, pays):
    """Valeur d'un chiffre officiel ; échoue si le chiffre manque (jamais de valeur inventée)."""
    row = ind[(ind["indicateur_id"] == indicateur) & (ind["pays_id"] == pays)]
    assert len(row) == 1, f"chiffre officiel manquant : {indicateur} / {pays}"
    return float(row["valeur"].iloc[0])


rows = []


def add(kpi_id, axe, kpi, valeur, unite, nature, formule, pays="", categorie="", zone="", annee=""):
    rows.append({"kpi_id": kpi_id, "axe": axe, "kpi": kpi, "pays_id": pays, "categorie_id": categorie,
                 "zone": zone, "annee": annee, "valeur": round(valeur, 2), "unite": unite,
                 "nature": nature, "formule": formule})


LAST = int(marche["annee"].max())  # 2025
dep = marche.set_index(["pays_id", "categorie_id", "annee"])["depenses_menages_meur"]

# --- Marché & Potentiel -------------------------------------------------------------------
for (pays, cat), serie in marche.groupby(["pays_id", "categorie_id"]):
    serie = serie.set_index("annee")["depenses_menages_meur"].sort_index()
    for annee, taux in (serie.pct_change() * 100).dropna().items():
        add("K1a", "Marché & Potentiel", "Taux de croissance annuel du secteur", taux, "%", "mesuré",
            "dépenses N / dépenses N-1 - 1", pays, cat, annee=int(annee))
    first, last = serie.index.min(), serie.index.max()
    cagr = ((serie[last] / serie[first]) ** (1 / (last - first)) - 1) * 100
    add("K1b", "Marché & Potentiel", f"Croissance annuelle moyenne {first}-{last}", cagr, "%", "mesuré",
        "(dépenses fin / dépenses début)^(1/nb années) - 1", pays, cat, annee=int(last))

# Parts de marché HT / HT (règle de gestion n° 9) : le CA est publié HT, les dépenses des ménages sont TTC
def ht(pays, cat):
    taux = v("tva_taux_normal", pays) if cat == "TECH" else v("tva_taux_reduit" if pays == "DE" else "tva_taux_reduit_le_plus_bas", pays)
    return dep[(pays, cat, LAST)] / (1 + taux / 100)


marche_fr_ht = ht("FR", "TECH") + ht("FR", "LIVRES")
part_fnac = (v("fnacdarty_part_ca_produits_techniques", "GROUPE") + v("fnacdarty_part_ca_produits_editoriaux", "GROUPE")) / 100
add("K2", "Marché & Potentiel", "Part de marché de Fnac Darty en France (HT / HT)", v("fnacdarty_ca_france", "FR") * part_fnac / marche_fr_ht * 100,
    "%", "estimation", "CA France HT × (part techniques + part éditoriaux du groupe) / dépenses FR (TECH + LIVRES) ramenées HT", "FR", annee=LAST)

marche_de_tech_ht = ht("DE", "TECH")
ventes_cec = v("ceconomy_ventes_allemagne", "DE")
add("K3_bas", "Marché & Potentiel", "Part de marché du concurrent CECONOMY en Allemagne, HT / HT (bas)",
    ventes_cec * v("ceconomy_part_ventes_it_mobile", "GROUPE") / 100 / marche_de_tech_ht * 100, "%", "estimation",
    "ventes DE HT × part « IT et mobile » / dépenses DE TECH ramenées HT", "DE", "TECH", annee=LAST)
add("K3_haut", "Marché & Potentiel", "Part de marché du concurrent CECONOMY en Allemagne, HT / HT (haut)",
    ventes_cec / marche_de_tech_ht * 100, "%", "estimation", "ventes DE HT / dépenses DE TECH ramenées HT", "DE", "TECH", annee=LAST)

# --- Prix & Marges ------------------------------------------------------------------------
# TVA : taux normal pour TECH ; taux réduit pour LIVRES (hypothèse : l'indice LIVRES = loisirs-culture, règle n° 8)
tva = {("DE", "TECH"): v("tva_taux_normal", "DE"), ("FR", "TECH"): v("tva_taux_normal", "FR"),
       ("DE", "LIVRES"): v("tva_taux_reduit", "DE"), ("FR", "LIVRES"): v("tva_taux_reduit_le_plus_bas", "FR")}
marge_groupe = v("fnacdarty_taux_marge_brute", "GROUPE") / 100
prix = marche.dropna(subset=["indice_niveau_prix_ue100"]).set_index(["pays_id", "categorie_id", "annee"])["indice_niveau_prix_ue100"]
for cat in ["TECH", "LIVRES"]:
    nature = "mesuré" if cat == "TECH" else "estimation"  # LIVRES : indice approximatif (loisirs-culture)
    for annee in sorted({a for (_, c, a) in prix.index if c == cat}):
        de, fr = prix[("DE", cat, annee)], prix[("FR", cat, annee)]
        add("K4_ttc", "Prix & Marges", "Indice de prix relatif DE / FR (TTC)", de / fr * 100, "indice FR = 100",
            nature, "indice DE / indice FR × 100", "DE", cat, annee=int(annee))
        ht = (de / (1 + tva[("DE", cat)] / 100)) / (fr / (1 + tva[("FR", cat)] / 100)) * 100
        add("K4_ht", "Prix & Marges", "Indice de prix relatif DE / FR (hors taxes)", ht, "indice FR = 100",
            nature, "(indice DE / (1 + TVA DE)) / (indice FR / (1 + TVA FR)) × 100", "DE", cat, annee=int(annee))
        add("K5", "Prix & Marges", "Marge brute estimée post-taxe en Allemagne", (1 - (1 - marge_groupe) / (ht / 100)) * 100,
            "%", "estimation", "1 - (1 - marge brute groupe) / (indice HT / 100), coût d'achat identique", "DE", cat, annee=int(annee))

# --- Réseau & Implantation ----------------------------------------------------------------
mag = magasins.merge(communes[["code_commune", "land_code"]], on="code_commune", how="left", validate="many_to_one")
pop_land = communes.groupby("land_code")["population"].sum()
nb_land = mag.groupby("land_code")["nb_magasins"].sum().reindex(pop_land.index, fill_value=0)
for land_code, nb in nb_land.items():
    nom = lands.set_index("land_code").loc[land_code, "land_nom"]
    add("K6", "Réseau & Implantation", "Densité concurrentielle (magasins CECONOMY par million d'habitants)",
        nb / pop_land[land_code] * 1e6, "magasins / M hab.", "mesuré", "magasins du Land / population du Land × 1 000 000",
        "DE", zone=nom, annee=2025)
add("K6", "Réseau & Implantation", "Densité concurrentielle (magasins CECONOMY par million d'habitants)",
    nb_land.sum() / pop_land.sum() * 1e6, "magasins / M hab.", "mesuré", "magasins / population × 1 000 000",
    "DE", zone="Allemagne", annee=2025)

loyer = v("loyer_reference_centre_ville", "DE")
add("K7", "Réseau & Implantation", "Coût moyen au m² commercial (loyer, centre-ville)", loyer * 12, "€/m²/an", "hypothèse",
    "loyer de référence IHK Stuttgart (115 €/m²/mois, unité mensuelle déduite) × 12", "DE", annee=2024)

# Pression concurrentielle nationale (borne haute, règle de gestion n° 11) : CECONOMY + Expert + Euronics
autres = pd.read_csv(SILVER / "concurrents_autres.csv")
pdv_autres = autres.loc[autres["canal"].eq("magasin"), "nb_points_de_vente"].sum()
pop_de = population.set_index(["pays_id", "annee"])["population_1er_janvier"][("DE", int(population["annee"].max()))]
add("K6_national", "Réseau & Implantation", "Pression concurrentielle nationale (borne haute)",
    (magasins["nb_magasins"].sum() + pdv_autres) / pop_de * 1e6, "points de vente / M hab.", "estimation",
    "(magasins CECONOMY + points de vente Expert + Euronics) / population DE × 1 000 000 ; formats non comparables",
    "DE", zone="Allemagne", annee=2025)

# --- Opérations & Logistique --------------------------------------------------------------
grandes = communes[communes["population"] >= 100_000]
add("K8", "Opérations & Logistique", "Distance moyenne depuis le hub de Chilly-Mazarin (villes ≥ 100 000 hab.)",
    (grandes["distance_hub_km"] * grandes["population"]).sum() / grandes["population"].sum(), "km", "mesuré",
    f"moyenne des distances à vol d'oiseau, pondérée par la population ({len(grandes)} villes)", "DE", annee=2025)
add("K9_douane", "Opérations & Logistique", "Droits de douane France -> Allemagne", v("droits_douane_intra_ue", "DE"), "%",
    "mesuré", "union douanière de l'UE (TFUE art. 28 et 30)", "DE", annee=2026)
for cat, (de_key, fr_key) in {"TECH": ("tva_taux_normal", "tva_taux_normal"),
                              "LIVRES": ("tva_taux_reduit", "tva_taux_reduit_le_plus_bas")}.items():
    add("K9_tva", "Opérations & Logistique", "Écart de TVA Allemagne - France", v(de_key, "DE") - v(fr_key, "FR"),
        "points de %", "mesuré", "TVA DE - TVA FR", "DE", cat, annee=2026)

# --- Assortiment --------------------------------------------------------------------------
pop = population.set_index(["pays_id", "annee"])["population_1er_janvier"]
for cat in ["TECH", "LIVRES"]:
    par_hab = {p: dep[(p, cat, LAST)] * 1e6 / pop[(p, LAST)] for p in ["DE", "FR"]}
    add("K10", "Assortiment", "Taux de pénétration de la catégorie en Allemagne (France = 100)",
        par_hab["DE"] / par_hab["FR"] * 100, "indice FR = 100", "mesuré",
        "(dépenses DE / population DE) / (dépenses FR / population FR) × 100", "DE", cat, annee=LAST)
    for p, valeur in par_hab.items():
        add("K10_detail", "Assortiment", "Dépenses par habitant", valeur, "€ / hab.", "mesuré", "dépenses / population", p, cat, annee=LAST)

catalogue = pd.read_csv(GOLD / "catalogue_simule.csv")
add("K11", "Assortiment", "% du catalogue France éligible en Allemagne", catalogue["eligible_allemagne"].mean() * 100,
    "%", "simulé", "références éligibles / références du catalogue simulé (règles dans catalogue_simule.py)", "DE", annee=2026)
for famille, part in catalogue.groupby("famille")["eligible_allemagne"].mean().items():
    add("K11_detail", "Assortiment", "% éligible par famille", part * 100, "%", "simulé", "idem, par famille",
        "DE", zone=famille, annee=2026)

# --- ★ Synthèse : délai de retour sur investissement d'un magasin (hors guide du prof) ------
# Quatre scénarios : marge (achats en France au prix allemand, ou achats locaux) × loyer (IHK ou niveau France).
h = pd.read_csv(SILVER / "hypotheses_roi.csv").set_index("parametre")["valeur"].astype(float)
ca_m2 = v("fnacdarty_ca_france", "FR") * 1e6 * (1 - h["part_ventes_en_ligne"] / 100) / h["surface_commerciale_france_m2"]
ca_magasin = ca_m2 * h["surface_magasin_m2"]
loyers_groupe_pct = (h["ebitda_courant_meur"] - h["ebitda_courant_hors_ifrs16_meur"]) / h["ca_groupe_meur"] * 100
ebitda_hors_loyer_pct = h["ebitda_courant_meur"] / h["ca_groupe_meur"] * 100
couts_hors_loyer_pct = marge_groupe * 100 - ebitda_hors_loyer_pct  # personnel, énergie, marketing… en % du CA
k5 = {r["categorie_id"]: r["valeur"] for r in rows if r["kpi_id"] == "K5" and r["annee"] == LAST}
poids = {"TECH": v("fnacdarty_part_ca_produits_techniques", "GROUPE"), "LIVRES": v("fnacdarty_part_ca_produits_editoriaux", "GROUPE")}
marge_de_achats_france = sum(k5[c] * poids[c] for c in poids) / sum(poids.values())
investissement = h["investissement_amenagement_eur_m2"] * h["surface_magasin_m2"]

add("K12_ca", "Synthèse", "CA annuel estimé d'un magasin (2 400 m²)", ca_magasin / 1e6, "M€", "estimation",
    "CA France × (1 - part en ligne) / surface commerciale France × surface d'un magasin", "DE", annee=LAST)
add("K12_invest", "Synthèse", "Investissement d'ouverture d'un magasin", investissement / 1e6, "M€", "hypothèse",
    "coût d'aménagement au m² (non sourcé) × surface", "DE", annee=LAST)
add("K7_magasin", "Réseau & Implantation", "Loyer annuel d'un magasin de 2 400 m² au loyer IHK", loyer * 12 * h["surface_magasin_m2"] / 1e6,
    "M€ / an", "hypothèse", "loyer de référence × 12 × surface d'un magasin", "DE", annee=2024)
for nom_seuil, loyer_max in {"loyer maximal pour un résultat positif (achats locaux)":
                             ca_magasin * (marge_groupe * 100 - couts_hors_loyer_pct) / 100 / h["surface_magasin_m2"] / 12}.items():
    add("K12_seuil_loyer", "Synthèse", nom_seuil.capitalize(), loyer_max, "€/m²/mois", "estimation",
        "CA × (marge 28 % - coûts hors loyer) / surface / 12", "DE", annee=LAST)
scenarios = {
    "A. achats France + loyer IHK": (marge_de_achats_france, loyer * 12 * h["surface_magasin_m2"]),
    "B. achats France + loyer niveau France": (marge_de_achats_france, loyers_groupe_pct / 100 * ca_magasin),
    "C. achats locaux + loyer IHK": (marge_groupe * 100, loyer * 12 * h["surface_magasin_m2"]),
    "D. achats locaux + loyer niveau France": (marge_groupe * 100, loyers_groupe_pct / 100 * ca_magasin),
}
for nom, (marge_pct, loyer_annuel) in scenarios.items():
    resultat = ca_magasin * (marge_pct - couts_hors_loyer_pct) / 100 - loyer_annuel
    add("K12_resultat", "Synthèse", "Résultat annuel estimé d'un magasin (avant amortissement)", resultat / 1e6, "M€",
        "estimation", "CA × (marge brute - coûts hors loyer) - loyer", "DE", zone=nom, annee=LAST)
    # Résultat négatif : le magasin ne rembourse jamais l'investissement -> délai noté 999 (= jamais)
    delai = investissement / resultat if resultat > 0 else 999
    add("K12", "Synthèse", "Délai de retour sur investissement d'un magasin (999 = jamais)", delai, "années",
        "estimation", "investissement / résultat annuel", "DE", zone=nom, annee=LAST)

# Sensibilité du scénario D (le seul positif) : CA au m² ± 20 % et investissement 1 000 / 1 500 / 2 000 €/m².
# K12 est un ordre de grandeur calculé sur des ratios du GROUPE (CA France, surfaces France y compris
# Nature & Découvertes, coûts groupe) : ni montée en charge, ni impôts, ni BFR, ni investissement de maintien.
loyer_d = scenarios["D. achats locaux + loyer niveau France"][1]
for ecart_ca in (-0.20, 0.0, 0.20):
    for invest_m2 in (1000, 1500, 2000):
        ca = ca_magasin * (1 + ecart_ca)
        resultat = ca * (marge_groupe * 100 - couts_hors_loyer_pct) / 100 - loyer_d * (1 + ecart_ca)
        delai = invest_m2 * h["surface_magasin_m2"] / resultat if resultat > 0 else 999
        add("K12_sensibilite", "Synthèse", "Délai de retour, scénario D, sensibilité (999 = jamais)", delai, "années",
            "estimation", "investissement / résultat annuel, loyer proportionnel au CA",
            "DE", zone=f"CA {ecart_ca:+.0%} ; invest {invest_m2} €/m²", annee=LAST)

kpi = pd.DataFrame(rows)
assert kpi["valeur"].map(math.isfinite).all(), "valeur non calculable"
kpi.to_csv(GOLD / "kpi.csv", index=False)
print(f"kpi.csv : {len(kpi)} lignes, {kpi['kpi_id'].nunique()} indicateurs")
