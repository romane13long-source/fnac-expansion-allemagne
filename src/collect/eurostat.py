"""Bronze : télécharge les séries Eurostat (API officielle, JSON-stat) sans les modifier.

Une seule source par sujet, même nomenclature (COICOP 2018) pour le marché et les prix :
- marché : dépenses des ménages par fonction (nama_10_cp18)
- prix   : indices de niveau des prix (prc_ppp_ind_1)
"""
import json
import urllib.parse

from paths import COUNTRIES, FIRST_YEAR, RAW, open_url

API = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

DATASETS = {
    # CP081 = équipements d'information et de communication ; CP097 = journaux, livres et papeterie
    "nama_10_cp18": {"coicop18": ["CP081", "CP097"], "unit": ["CP_MEUR"]},
    # A010801 = même catégorie que CP081 ; A0109 = loisirs, sport et culture (livres non isolés)
    "prc_ppp_ind_1": {"ppp_cat18": ["A010801", "A0109"], "indic_ppp": ["PLI_EU27_2020"]},
}


def download(code, filters):
    params = [("geo", c) for c in COUNTRIES] + [("sinceTimePeriod", FIRST_YEAR)]
    params += [(dim, value) for dim, values in filters.items() for value in values]
    url = f"{API}/{code}?{urllib.parse.urlencode(params)}"
    with open_url(url) as response:
        data = json.load(response)
    if "error" in data:
        raise RuntimeError(f"{code} : {data['error']}")
    return data


if __name__ == "__main__":
    for code, filters in DATASETS.items():
        data = download(code, filters)
        (RAW / f"eurostat_{code}.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        print(f"eurostat_{code}.json : {len(data['value'])} valeurs, mis à jour le {data.get('updated')}")
