"""Données de restitution, lues dans le Gold : partagées par le dashboard, les slides et la brique IA.

Aucun calcul de KPI ici (ils sont dans src/gold/kpi.py) : on regroupe seulement ce qu'il faut afficher.
"""
import pandas as pd

from paths import GOLD, SILVER

kpi = pd.read_csv(GOLD / "kpi.csv", keep_default_na=False)
marche = pd.read_csv(GOLD / "fact_marche.csv")
communes = pd.read_csv(GOLD / "dim_commune.csv", dtype={"code_commune": str, "land_code": str})
lands = pd.read_csv(GOLD / "dim_land.csv", dtype={"land_code": str})
magasins = pd.read_csv(GOLD / "fact_magasins_concurrents.csv", dtype={"code_commune": str})
hyp = pd.read_csv(SILVER / "hypotheses_roi.csv").set_index("parametre")["valeur"].astype(float)
ind = pd.read_csv(GOLD / "fact_indicateurs_officiels.csv")
autres = pd.read_csv(SILVER / "concurrents_autres.csv")

LAST = int(kpi.loc[kpi["kpi_id"].eq("K1a"), "annee"].max())


def val(kid, zone="", cat="", pays="DE", annee=None):
    """Une valeur de kpi.csv ; la dernière année si plusieurs. Échoue si absente (jamais de valeur inventée)."""
    rows = kpi[(kpi.kpi_id == kid) & (kpi.zone == zone) & (kpi.categorie_id == cat) & (kpi.pays_id == pays)]
    if annee is not None:
        rows = rows[rows.annee == annee]
    assert len(rows), f"KPI introuvable : {kid} {pays} {cat} {zone} {annee}"
    return float(rows.sort_values("annee")["valeur"].iloc[-1])


def officiel(indicateur, pays):
    return float(ind[(ind.indicateur_id == indicateur) & (ind.pays_id == pays)]["valeur"].iloc[0])


def table_lands():
    """Une ligne par Land : population, magasins CECONOMY, densité (K6), plus grande ville et sa distance au hub."""
    mag = magasins.merge(communes[["code_commune", "land_code"]], on="code_commune")
    nb = mag.groupby("land_code").size()
    out = []
    for land in lands.itertuples():
        c = communes[communes.land_code == land.land_code]
        ville = c.sort_values("population").iloc[-1]
        out.append({
            "land": land.land_nom, "population": int(c.population.sum()), "magasins": int(nb.get(land.land_code, 0)),
            "densite": val("K6", zone=land.land_nom),
            "ville": ville["nom"].split(",")[0], "ville_pop": int(ville.population),
            "ville_km": float(ville.distance_hub_km),
            "villes_100k": int((c.population >= 100_000).sum()),
            # Marché potentiel du Land (estimation) : dépenses nationales × part de la population, même dépense par habitant
            "part_pop": float(c.population.sum() / communes.population.sum() * 100),
            "marche_tech": float(dep_last("TECH") * c.population.sum() / communes.population.sum()),
            "marche_livres": float(dep_last("LIVRES") * c.population.sum() / communes.population.sum()),
            "villes": [{"nom": v["nom"].split(",")[0], "pop": int(v.population), "km": float(v.distance_hub_km),
                        "magasins": int(nb_com.get(v.code_commune, 0))}
                       for _, v in c.sort_values("population", ascending=False).head(8).iterrows()],
        })
    return out


def dep_last(cat):
    return float(marche[(marche.pays_id == "DE") & (marche.categorie_id == cat) & (marche.annee == LAST)]["depenses_menages_meur"].iloc[0])


nb_com = magasins.groupby("code_commune").size()


def carte():
    """Points de la carte : communes de 5 000 hab. et plus (fond), magasins CECONOMY, villes de 100 000 hab. et plus."""
    land_nom = lands.set_index("land_code")["land_nom"]
    fond = communes[communes.population >= 5000]
    mag = magasins.merge(communes[["code_commune", "nom", "longitude", "latitude", "land_code"]], on="code_commune")
    villes = communes[communes.population >= 100_000]
    return {
        "fond": [[round(r.longitude, 2), round(r.latitude, 2), land_nom[r.land_code]] for r in fond.itertuples()],
        "magasins": [[round(r.longitude, 3), round(r.latitude, 3), land_nom[r.land_code], r.nom.split(",")[0], r.enseigne] for r in mag.itertuples()],
        "villes": [{"nom": r.nom.split(",")[0], "lon": r.longitude, "lat": r.latitude, "pop": int(r.population), "km": float(r.distance_hub_km),
                    "land": land_nom[r.land_code], "magasins": int(nb_com.get(r.code_commune, 0))} for r in villes.itertuples()],
    }


SCENARIOS = {
    "A": "A. achats France + loyer IHK", "B": "B. achats France + loyer niveau France",
    "C": "C. achats locaux + loyer IHK", "D": "D. achats locaux + loyer niveau France",
}


def haversine_km(lon1, lat1, lon2, lat2):
    import math
    lon1, lat1, lon2, lat2 = map(math.radians, (lon1, lat1, lon2, lat2))
    a = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(a))


VILLES_CANDIDATES = 7  # les 7 plus grandes villes : assez pour comparer, peu pour rester lisible


def villes_candidates():
    """Les 7 plus grandes villes d'Allemagne, avec ce qu'il faut pour choisir où ouvrir."""
    pop_de = communes.population.sum()
    land_nom = lands.set_index("land_code")["land_nom"]
    koln = communes[communes.nom.str.startswith("Köln")].iloc[0]
    out = []
    for v in communes.sort_values("population", ascending=False).head(VILLES_CANDIDATES).itertuples():
        nom = v.nom.split(",")[0]
        out.append({
            "ville": nom, "land": land_nom[v.land_code], "pop": int(v.population),
            "part_pop": float(v.population / pop_de * 100),
            "magasins": int(nb_com.get(v.code_commune, 0)),
            "magasins_par_100k": float(nb_com.get(v.code_commune, 0) / v.population * 1e5),
            "densite_land": val("K6", zone=land_nom[v.land_code]),
            "km_hub": float(v.distance_hub_km),
            "km_koln": round(haversine_km(koln.longitude, koln.latitude, v.longitude, v.latitude), 1),
            # Marché potentiel de la ville (estimation) : population × dépense nationale par habitant
            "marche_tech": float(v.population * val("K10_detail", cat="TECH") / 1e6),
            "marche_livres": float(v.population * val("K10_detail", cat="LIVRES") / 1e6),
        })
    return out


def distance_moyenne_depuis(lon, lat):
    g = communes[communes.population >= 100_000]
    d = [haversine_km(lon, lat, r.longitude, r.latitude) for r in g.itertuples()]
    return float(sum(x * p for x, p in zip(d, g.population)) / g.population.sum())


def donnees():
    cats = ["TECH", "LIVRES"]
    par_cat = {}
    for cat in cats:
        serie = marche[marche.categorie_id == cat]
        par_cat[cat] = {
            "depenses": {p: {int(r.annee): r.depenses_menages_meur for r in serie[serie.pays_id == p].itertuples()} for p in ("DE", "FR")},
            "croissance_moy": {p: val("K1b", cat=cat, pays=p) for p in ("DE", "FR")},
            "croissance_last": {p: val("K1a", cat=cat, pays=p) for p in ("DE", "FR")},
            "indice_ht": {int(r.annee): r.valeur for r in kpi[(kpi.kpi_id == "K4_ht") & (kpi.categorie_id == cat)].itertuples()},
            "indice_ttc": {int(r.annee): r.valeur for r in kpi[(kpi.kpi_id == "K4_ttc") & (kpi.categorie_id == cat)].itertuples()},
            "marge": {int(r.annee): r.valeur for r in kpi[(kpi.kpi_id == "K5") & (kpi.categorie_id == cat)].itertuples()},
            "penetration": val("K10", cat=cat),
            "par_hab": {p: val("K10_detail", cat=cat, pays=p) for p in ("DE", "FR")},
            "tva": {"DE": val("K9_tva", cat=cat)},
        }
    scen = {k: {"nom": v, "resultat": val("K12_resultat", zone=v), "delai": val("K12", zone=v)} for k, v in SCENARIOS.items()}
    ca_magasin = val("K12_ca") * 1e6
    ebitda_pct = hyp["ebitda_courant_meur"] / hyp["ca_groupe_meur"] * 100
    loyers_pct = (hyp["ebitda_courant_meur"] - hyp["ebitda_courant_hors_ifrs16_meur"]) / hyp["ca_groupe_meur"] * 100
    marge_groupe = officiel("fnacdarty_taux_marge_brute", "GROUPE")
    poids = {"TECH": officiel("fnacdarty_part_ca_produits_techniques", "GROUPE"),
             "LIVRES": officiel("fnacdarty_part_ca_produits_editoriaux", "GROUPE")}
    pop_an = {(r.pays_id, int(r.annee)): r.population_1er_janvier for r in pd.read_csv(GOLD / "fact_population.csv").itertuples()}
    return {
        "last": LAST,
        "categories": par_cat,
        "parts": {"fnac_fr": val("K2", pays="FR"), "cec_bas": val("K3_bas", cat="TECH"), "cec_haut": val("K3_haut", cat="TECH")},
        "lands": table_lands(),
        "densite_de": val("K6", zone="Allemagne"),
        "pression_nationale": val("K6_national", zone="Allemagne"),
        "concurrents": [{"enseigne": "MediaMarkt + Saturn", "pdv": int(len(magasins))}] +
                       [{"enseigne": r.enseigne, "pdv": int(r.nb_points_de_vente)} for r in autres.itertuples()],
        "loyer_m2_mois": officiel("loyer_reference_centre_ville", "DE"),
        "loyer_magasin": val("K7_magasin"),
        "distance_moy": val("K8"),
        "douane": val("K9_douane"),
        "eligible": val("K11"),
        "eligible_familles": {r.zone: r.valeur for r in kpi[kpi.kpi_id == "K11_detail"].itertuples()},
        "scenarios": scen,
        "seuil_loyer": val("K12_seuil_loyer"),
        "transport": {n: {"trajet": val("K8_transport", zone=n), "an": val("K8_transport_an", zone=n),
                          "delai": val("K12_avec_transport", zone=n)} for n in ("bas", "haut")},
        "livraisons_an": int(hyp["livraisons_france_par_an"]),
        # paramètres du simulateur : mêmes formules que src/gold/kpi.py
        "simu": {
            "ca_magasin": ca_magasin, "surface": hyp["surface_magasin_m2"], "invest_m2": hyp["investissement_amenagement_eur_m2"],
            "couts_hors_loyer_pct": marge_groupe - ebitda_pct, "loyers_pct": loyers_pct, "marge_locale": marge_groupe,
            "marge_achats_france": sum(par_cat[c]["marge"][LAST] * poids[c] for c in cats) / sum(poids.values()),
        },
        "x_magasins_fr": 205,
        "villes": villes_candidates(),
        "par_hab_annees": {cat: {p: {int(r.annee): float(r.depenses_menages_meur * 1e6 / pop_an[(p, int(r.annee))])
                                     for r in marche[(marche.pays_id == p) & (marche.categorie_id == cat)].itertuples() if (p, int(r.annee)) in pop_an}
                                 for p in ("DE", "FR")} for cat in ("TECH", "LIVRES")},
        "prix_ue": {cat: {p: {int(r.annee): float(r.indice_niveau_prix_ue100)
                              for r in marche[(marche.pays_id == p) & (marche.categorie_id == cat)].dropna(subset=["indice_niveau_prix_ue100"]).itertuples()}
                          for p in ("DE", "FR")} for cat in ("TECH", "LIVRES")},
        "cec_ventes": {2024: officiel("ceconomy_ventes_allemagne_n1", "DE"), 2025: officiel("ceconomy_ventes_allemagne", "DE")},
        "marche_tech_ht": {y: float(marche[(marche.pays_id == "DE") & (marche.categorie_id == "TECH") & (marche.annee == y)]["depenses_menages_meur"].iloc[0]
                                    / (1 + officiel("tva_taux_normal", "DE") / 100)) for y in (2024, 2025)},
        "finances": {k: officiel(f"fnacdarty_{k}", "GROUPE") for k in (
            "cash_flow_libre_operationnel", "cash_flow_libre_operationnel_n1", "investissements_operationnels", "tresorerie_nette",
            "resultat_net_part_groupe", "resultat_operationnel_courant", "capex_moyen_plan", "cash_flow_libre_cumule_plan", "taux_marge_brute")},
        "distance_depuis_koln": distance_moyenne_depuis(*communes[communes.nom.str.startswith("Köln")][["longitude", "latitude"]].iloc[0]),
        "tva": {"DE": officiel("tva_taux_normal", "DE"), "FR": officiel("tva_taux_normal", "FR"),
                "DE_reduit": officiel("tva_taux_reduit", "DE"), "FR_reduit": officiel("tva_taux_reduit_le_plus_bas", "FR")},
        "carte": carte(),
    }
