"""Bronze -> Silver : transforme les réponses JSON-stat d'Eurostat en tables propres (une ligne = un pays, une année, une catégorie)."""
import json

import pandas as pd

from paths import COUNTRIES, RAW, SILVER

# Eurostat marque certaines valeurs : p = provisoire, e = estimée, b = rupture de série
STATUS_LABELS = {"p": "provisoire", "e": "estimée", "b": "rupture de série", "d": "définition différente"}


def jsonstat_to_frame(data):
    """Déplie le cube JSON-stat : l'index plat d'une valeur se décode dimension par dimension."""
    ids, sizes = data["id"], data["size"]
    codes = [sorted(data["dimension"][d]["category"]["index"], key=data["dimension"][d]["category"]["index"].get)
             for d in ids]
    statuses = data.get("status", {})
    rows = []
    for key, value in data["value"].items():
        flat, position = int(key), {}
        for dim, size, dim_codes in zip(reversed(ids), reversed(sizes), reversed(codes)):
            position[dim] = dim_codes[flat % size]
            flat //= size
        position["value"] = value
        position["status"] = STATUS_LABELS.get(statuses.get(key, ""), statuses.get(key, ""))
        rows.append(position)
    return pd.DataFrame(rows), {d: data["dimension"][d]["category"]["label"] for d in ids}


def load(code):
    data = json.loads((RAW / f"eurostat_{code}.json").read_text(encoding="utf-8"))
    return jsonstat_to_frame(data)


def tidy(frame, labels, category_dim, value_name):
    out = pd.DataFrame({
        "pays": frame["geo"],
        "annee": frame["time"].astype(int),
        "categorie_code": frame[category_dim],
        "categorie": frame[category_dim].map(labels[category_dim]),
        value_name: frame["value"].astype(float),
        "statut_eurostat": frame["status"],
    }).sort_values(["categorie_code", "pays", "annee"]).reset_index(drop=True)
    # Contrôles : les deux pays, aucune valeur négative, pas de doublon
    assert set(out["pays"]) == set(COUNTRIES), f"pays manquant : {set(COUNTRIES) - set(out['pays'])}"
    assert (out[value_name] >= 0).all(), "valeur négative"
    assert not out.duplicated(["pays", "annee", "categorie_code"]).any(), "doublon pays / année / catégorie"
    return out


if __name__ == "__main__":
    market, labels = load("nama_10_cp18")
    market = tidy(market, labels, "coicop18", "depenses_menages_meur")
    market.to_csv(SILVER / "marche.csv", index=False)

    prices, labels = load("prc_ppp_ind_1")
    prices = tidy(prices, labels, "ppp_cat18", "indice_niveau_prix_ue100")
    prices.to_csv(SILVER / "prix.csv", index=False)

    for name, table in {"marche": market, "prix": prices}.items():
        flagged = (table["statut_eurostat"] != "").sum()
        print(f"{name}.csv : {len(table)} lignes, {table['annee'].min()}-{table['annee'].max()}, "
              f"{flagged} valeurs signalées par Eurostat")
