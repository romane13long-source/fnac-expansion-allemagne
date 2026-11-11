"""Bronze -> Silver : rattache chaque magasin MediaMarkt / Saturn à une commune allemande (Destatis).

La seule information de localisation est le nom de la page du magasin, par exemple
« muehldorf-am-inn-579 » ou « berlin-mitte-190 ». La clé de jointure avec les communes
est donc le nom de la ville, qu'il faut rendre comparable des deux côtés.
"""
import re
import unicodedata
from urllib.parse import unquote

import pandas as pd

from paths import MANUAL, RAW, SILVER

# Destatis abrège les prépositions : « Mühldorf a.Inn », « Frankfurt a.Main », « Neumarkt i.d.OPf. »
ABBREVIATIONS = {"a.d.": "an der ", "i.d.": "in der ", "a.": "am ", "i.": "im ", "b.": "bei ", "v.d.": "vor der "}
# Mots ajoutés par l'enseigne devant le nom de la ville (formats de magasin, centres commerciaux)
SHOP_PREFIXES = ("smart-", "tech-village-", "stadtgalerie-", "boulevard-")
# Premiers mots partagés par des dizaines de communes : jamais suffisants seuls pour rattacher un magasin
GENERIC_WORDS = {"bad", "sankt", "st", "neu", "alt", "gross", "klein"}


def normalize(name):
    """Met un nom au même format que les adresses web : minuscules, ä -> ae, mots séparés par des tirets."""
    name = name.split(",")[0]                       # « Kiel, Landeshauptstadt » -> « Kiel »
    name = re.sub(r"\(.*?\)", "", name)              # retire les précisions entre parenthèses
    for short, long in ABBREVIATIONS.items():
        name = name.replace(short, long)
    name = name.lower()
    for umlaut, ascii_ in {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}.items():
        name = name.replace(umlaut, ascii_)
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", name).strip("-")


def store_rows(brand):
    xml = (RAW / f"sitemap_{brand}.xml").read_text(encoding="utf-8")
    # Certaines adresses gardent les accents encodés : « m%C3%BCnchen » = « münchen »
    slugs = [unquote(s) for s in re.findall(r"/de/store/([^<]+)</loc>", xml)]
    rows = []
    for slug in slugs:
        match = re.fullmatch(r"(.+?)-(\d+)", slug.replace("_", "-"))
        if match is None:          # « region-kassel » : page de région, pas un magasin
            continue
        name = normalize(match.group(1))
        for prefix in SHOP_PREFIXES:
            name = name.removeprefix(prefix)
        rows.append({"enseigne": brand, "magasin_id": int(match.group(2)), "page": slug, "nom_page": name})
    return pd.DataFrame(rows), len(slugs)


communes = pd.read_csv(SILVER / "communes.csv", dtype={"code_commune": str, "land_code": str})
communes["cle"] = communes["nom"].map(normalize)
# Plusieurs communes portent le même nom (ex. Neustadt) : on garde la plus peuplée, la plus probable pour un magasin
lookup = communes.sort_values("population", ascending=False).drop_duplicates("cle").set_index("cle")
assert lookup.index.is_unique


# Table manuelle : pour les noms de centres commerciaux, on désigne la commune par son code officiel (sans ambiguïté)
aliases = pd.read_csv(MANUAL / "alias_magasins.csv", dtype=str).set_index("page")["code_commune"]
key_by_code = communes.set_index("code_commune")["cle"]
assert aliases.isin(key_by_code.index).all(), "code commune inconnu dans alias_magasins.csv"


def find_commune(row):
    """Renvoie (clé de la commune, méthode), du rattachement le plus sûr au moins sûr."""
    if row["page"] in aliases.index:                       # 1. table de correspondance tenue à la main
        return key_by_code[aliases[row["page"]]], "table manuelle"
    words = row["nom_page"].split("-")
    for n in range(len(words), 0, -1):                     # 2. « berlin-mitte » -> « berlin »
        key = "-".join(words[:n])
        if key in lookup.index:
            return key, "nom exact"
    # 3. « brandenburg » -> « brandenburg-an-der-havel », « dessau-city » -> « dessau-rosslau » :
    #    on raccourcit le nom de page mot à mot, sans jamais s'arrêter sur un mot générique seul
    #    (« bad-neustadt » ne doit pas devenir « Bad Homburg »)
    for n in range(len(words), 0, -1):
        if n == 1 and words[0] in GENERIC_WORDS:
            break
        starts = lookup.index[lookup.index.str.startswith("-".join(words[:n]) + "-")]
        if len(starts):                                    # lookup est trié par population : la plus peuplée
            return starts[0], "début du nom officiel"
    return None, None


tables, report = [], []
for brand in ["mediamarkt", "saturn"]:
    stores, total = store_rows(brand)
    assert not stores.duplicated("magasin_id").any(), f"{brand} : identifiant de magasin en double"
    stores[["cle", "methode_rattachement"]] = stores.apply(find_commune, axis=1, result_type="expand")
    report.append(f"{brand} : {total} adresses, {total - len(stores)} pages de région retirées, "
                  f"{len(stores)} magasins, {stores['cle'].isna().sum()} sans commune trouvée")
    tables.append(stores)

stores = pd.concat(tables, ignore_index=True)
# Un même magasin (même identifiant) peut être listé sur les deux sites : MediaMarkt et Saturn forment
# un seul concurrent (CECONOMY), on le compte une fois
shared = stores["magasin_id"].duplicated(keep=False)
stores["liste_sur_les_deux_sites"] = shared
stores = stores.drop_duplicates("magasin_id", keep="first")
report.append(f"{shared.sum() // 2} magasins listés sur les deux sites, comptés une fois : {len(stores)} magasins uniques "
              f"(rapport annuel CECONOMY : 344 MediaMarkt + 59 Saturn = 403)")
unmatched = stores[stores["cle"].isna()]
stores = stores.dropna(subset=["cle"]).join(
    lookup[["code_commune", "nom", "land_code", "land_nom", "longitude", "latitude"]], on="cle")
stores = stores.rename(columns={"nom": "commune"}).drop(columns="cle")

stores.to_csv(SILVER / "magasins_concurrents.csv", index=False)
unmatched[["enseigne", "magasin_id", "page"]].to_csv(SILVER / "magasins_non_rattaches.csv", index=False)
print("\n".join(report))
print(stores["methode_rattachement"].value_counts().to_string())
print(f"magasins_concurrents.csv : {len(stores)} magasins rattachés à une commune ; "
      f"non rattachés : {', '.join(unmatched['page']) or 'aucun'}")
