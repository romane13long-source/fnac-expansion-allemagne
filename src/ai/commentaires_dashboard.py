"""Brique IA (slide 5) : un commentaire par filtre ET par élément survolé du dashboard, rédigé par Claude (`claude -p`).

Groupes de commentaires (clé -> texte) :
- axes        « TECH|Marché & Potentiel » : catégorie × axe du guide des KPI (slide 7)
- scenarios   « A » … « D » : scénarios du ROI
- lands       « Bayern » … : les 16 zones de chalandise
- villes      « München » … : les villes de plus de 500 000 habitants (survol de la carte)
- marche      « TECH|2024 » : chaque année de la courbe des dépenses (survol)
- prix        « TECH|2024 » : chaque année de l'indice de prix et de la marge (survol)
- familles    « TECH » … : familles du catalogue simulé (survol)
- concurrents « Expert » … : enseignes concurrentes (survol)
Tout est généré au build, en deux appels parallèles (rien ne dépend d'internet pendant l'oral). Chaque commentaire est
contrôlé : tout nombre écrit doit figurer dans les faits envoyés à l'IA ; sinon il est remplacé par une phrase
déterministe, marquée « sans IA ».

Sortie : data/gold/commentaires_ia_filtres.json
Lancement : PYTHONPATH=src .venv/bin/python src/ai/commentaires_dashboard.py [--sans-ia]
"""
import json
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "restitution"))
import donnees  # noqa: E402

from paths import GOLD  # noqa: E402

MODELE = "sonnet"
AXES = ["Marché & Potentiel", "Prix & Marges", "Réseau & Implantation", "Opérations & Logistique", "Assortiment"]
D = donnees.donnees()
L = D["last"]
CATS = {"TECH": "produits techniques", "LIVRES": "livres, presse et papeterie"}
FAMILLES = {"TECH": "produits techniques", "JEUX_VIDEO": "jeux vidéo", "MUSIQUE_VIDEO": "musique et vidéo", "LIVRES": "livres"}


def f(x, d=1):
    s = f"{x:,.{d}f}".replace(",", " ").replace(".", ",")
    return s[:-2] if s.endswith(",0") else s


# ------------------------------------------------------------------ faits : clé -> phrase (seuls nombres permis)
def faits():
    F = {g: {} for g in ("axes", "scenarios", "lands", "villes", "marche", "prix", "familles", "concurrents")}
    for cat in CATS:
        c = D["categories"][cat]
        base = {
            "Marché & Potentiel": f"{CATS[cat]} : croissance annuelle moyenne 2015-{L} Allemagne {f(c['croissance_moy']['DE'])} %, France {f(c['croissance_moy']['FR'])} % ; "
                                  f"dépenses {L} Allemagne {f(c['depenses']['DE'][L], 0)} M€, France {f(c['depenses']['FR'][L], 0)} M€ ; "
                                  f"part de marché CECONOMY sur la tech {f(D['parts']['cec_bas'])} à {f(D['parts']['cec_haut'])} % (estimation) ; "
                                  f"part de marché Fnac Darty en France {f(D['parts']['fnac_fr'])} % (estimation)",
            "Prix & Marges": f"{CATS[cat]} : indice de prix hors taxes Allemagne/France {L} {f(c['indice_ht'][L])} (France = 100) ; "
                             f"marge brute en Allemagne à coût d'achat français {f(c['marge'][L])} % (estimation) contre 28 % pour le groupe",
            "Réseau & Implantation": f"densité CECONOMY {f(D['densite_de'])} magasins par million d'habitants ; pression nationale tous réseaux "
                                     f"{f(D['pression_nationale'])} (estimation) ; loyer de référence IHK {f(D['loyer_m2_mois'], 0)} €/m²/mois (hypothèse)",
            "Opérations & Logistique": f"distance moyenne pondérée au hub de Chilly-Mazarin {f(D['distance_moy'], 0)} km ; droits de douane 0 % ; "
                                       f"écart de TVA Allemagne - France {f(c['tva']['DE'])} point",
            "Assortiment": f"{CATS[cat]} : dépense par habitant {L} Allemagne {f(c['par_hab']['DE'], 0)} €, France {f(c['par_hab']['FR'], 0)} € ; "
                           f"pénétration {f(c['penetration'], 0)} (France = 100) ; catalogue éligible {f(D['eligible'])} % (simulé)",
        }
        for axe, phrase in base.items():
            F["axes"][f"{cat}|{axe}"] = phrase
        years = sorted(c["depenses"]["DE"])
        for y0, y in zip(years, years[1:]):
            de, fr = c["depenses"]["DE"], c["depenses"]["FR"]
            F["marche"][f"{cat}|{y}"] = (f"{CATS[cat]} en {y} : Allemagne {f(de[y], 0)} M€ ({f((de[y] / de[y0] - 1) * 100)} % sur un an), "
                                         f"France {f(fr[y], 0)} M€ ({f((fr[y] / fr[y0] - 1) * 100)} % sur un an)")
        for y in sorted(c["indice_ht"]):
            F["prix"][f"{cat}|{y}"] = (f"{CATS[cat]} en {y} : indice de prix hors taxes {f(c['indice_ht'][y])} (France = 100), "
                                       f"marge brute estimée {f(c['marge'][y])} % (estimation) contre 28 % pour le groupe")
    for k, s in D["scenarios"].items():
        F["scenarios"][k] = (f"{s['nom']} : résultat annuel {f(s['resultat'], 2)} M€ ; délai de retour " +
                             ("jamais" if s["delai"] >= 999 else f"{f(s['delai'])} ans") +
                             f" ; seuil de loyer avec achats locaux {f(D['seuil_loyer'])} €/m²/mois ; investissement 3,6 M€ (hypothèse)")
    for x in D["lands"]:
        F["lands"][x["land"]] = (f"{x['land']} : {f(x['densite'])} magasins CECONOMY par million d'habitants (moyenne {f(D['densite_de'])}), "
                                 f"{x['magasins']} magasins, {f(x['population'] / 1e6)} M habitants ({f(x['part_pop'])} % du pays), "
                                 f"marché tech potentiel {f(x['marche_tech'], 0)} M€ (estimation) ; plus grande ville {x['ville']} à {f(x['ville_km'], 0)} km du hub")
    for v in D["carte"]["villes"]:
        if v["pop"] >= 500_000:
            F["villes"][v["nom"]] = (f"{v['nom']} ({v['land']}) : {f(v['pop'] / 1e6, 2)} M habitants, {v['magasins']} magasins CECONOMY, "
                                     f"{f(v['km'], 0)} km du hub de Chilly-Mazarin")
    for k, v in D["eligible_familles"].items():
        F["familles"][k] = f"{FAMILLES[k]} : {f(v)} % des références éligibles en Allemagne (simulé) ; catalogue total {f(D['eligible'])} %"
    for k in D["concurrents"]:
        F["concurrents"][k["enseigne"]] = (f"{k['enseigne']} : {f(k['pdv'], 0)} points de vente en Allemagne" if k["pdv"]
                                          else f"{k['enseigne']} : vente en ligne seulement, aucun magasin")
    # Un commentaire par KPI du guide (vue d'ensemble du dashboard)
    t = D["categories"]["TECH"]
    sd = D["scenarios"]["D"]
    F["kpi"] = {
        "K1": f"croissance annuelle moyenne des dépenses tech 2015-{L} : Allemagne {f(t['croissance_moy']['DE'])} %, France {f(t['croissance_moy']['FR'])} %",
        "K2": f"part de marché de Fnac Darty en France {f(D['parts']['fnac_fr'])} % (estimation, HT/HT)",
        "K3": f"part de marché de CECONOMY sur la tech en Allemagne {f(D['parts']['cec_bas'])} à {f(D['parts']['cec_haut'])} % (estimation)",
        "K4": f"indice de prix tech hors taxes Allemagne/France {f(t['indice_ht'][L])} (France = 100)",
        "K5": f"marge brute tech en Allemagne à coût d'achat français {f(t['marge'][L])} % (estimation) contre 28 % pour le groupe",
        "K6": f"densité CECONOMY {f(D['densite_de'])} magasins par million d'habitants en Allemagne, de {f(min(x['densite'] for x in D['lands']))} à {f(max(x['densite'] for x in D['lands']))} selon le Land",
        "K7": f"loyer de référence IHK {f(D['loyer_m2_mois'], 0)} €/m²/mois soit {f(D['loyer_magasin'])} M€ par an pour 2 400 m² (hypothèse) ; seuil de rentabilité {f(D['seuil_loyer'])} €/m²/mois",
        "K8": f"distance moyenne pondérée au hub de Chilly-Mazarin {f(D['distance_moy'], 0)} km",
        "K9": f"droits de douane 0 % ; écart de TVA tech Allemagne - France {f(t['tva']['DE'])} point",
        "K10": f"pénétration tech {f(t['penetration'], 0)} (France = 100) ; livres {f(D['categories']['LIVRES']['penetration'], 0)}",
        "K11": f"part du catalogue France éligible en Allemagne, toutes familles confondues : {f(D['eligible'])} % (simulé) ; par famille : produits techniques {f(D['eligible_familles']['TECH'])} %, jeux vidéo {f(D['eligible_familles']['JEUX_VIDEO'])} %, livres {f(D['eligible_familles']['LIVRES'])} %",
        "K12": f"délai de retour d'un magasin : {f(sd['delai'])} ans dans le seul scénario rentable (achats locaux, loyer niveau France), jamais dans les 3 autres (estimation)",
    }
    return F


FAITS = faits()


def nombres(texte):
    texte = re.sub(r"(?<=\d)[  ](?=\d{3}\b)", "", texte)
    return [float(n.replace(",", ".")) for n in re.findall(r"\d+(?:,\d+)?", texte)]


AUTORISES = {round(x, d) for g in FAITS.values() for t in g.values() for x in nombres(t) for d in (0, 1, 2)} \
    | {0, 1, 2, 3, 4, 100, 2027, 2029} | set(range(2015, L + 1))


def valide(texte):
    return all(any(abs(n - a) < 0.051 for a in AUTORISES) for n in nombres(texte))


CONTEXTE = """Tu rédiges les commentaires d'un dashboard pour le Comex de la Fnac, qui étudie une implantation en Allemagne.
Décision de l'équipe : Go sous conditions, un magasin pilote à Cologne (Nordrhein-Westfalen), achats via une centrale allemande,
loyer sous le seuil, assortiment produits techniques + jeux vidéo, décision de déploiement après 2 ans.

Règles : français, 1 à 2 phrases courtes par commentaire, ton factuel pour des décideurs. Chaque commentaire cite 1 ou 2 chiffres
du fait correspondant ET dit ce que cela implique pour la décision (où ouvrir, quoi vendre, à quelle condition).
N'utilise QUE les nombres des faits (virgule décimale). Écris « (estimation) », « (hypothèse) » ou « (simulé) » quand le fait le dit.
Réponds UNIQUEMENT avec un objet JSON valide, sans texte autour : mêmes groupes et mêmes clés que les faits, valeur = commentaire.
N'utilise jamais de guillemets droits (") dans les commentaires : utilise « » si besoin.
"""
LOTS = [("axes", "scenarios", "lands", "familles", "concurrents"), ("villes", "marche", "prix", "kpi")]


def appeler_claude(groupes, essais=2):
    for essai in range(1, essais + 1):
        try:
            return _appel(groupes)
        except (ValueError, json.JSONDecodeError) as e:  # JSON mal formé : on redemande une fois
            if essai == essais:
                raise
            print(f"lot {groupes} : réponse illisible ({e}), nouvel essai")


def _appel(groupes):
    prompt = CONTEXTE + "\nFaits :\n" + json.dumps({g: FAITS[g] for g in groupes}, ensure_ascii=False, indent=1)
    r = subprocess.run(["claude", "-p", "--model", MODELE, "--tools", "", "--no-session-persistence",
                        "--output-format", "text", "--setting-sources", "project"],
                       input=prompt, capture_output=True, text=True, timeout=900)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:300])
    m = re.search(r"\{.*\}", r.stdout, re.S)
    if not m:
        raise ValueError("pas de JSON dans la réponse")
    return json.loads(m.group(0))


ia = {}
if "--sans-ia" not in sys.argv and shutil.which("claude"):
    with ThreadPoolExecutor(len(LOTS)) as pool:
        for lot, fut in zip(LOTS, [pool.submit(appeler_claude, lot) for lot in LOTS]):
            try:
                ia.update(fut.result())
            except Exception as e:
                print(f"lot {lot} : appel à Claude impossible ({e}) -> texte sans IA")

resultat, rejets = {}, []
for g, cles in FAITS.items():
    resultat[g] = {}
    for cle, fait in cles.items():
        propose = (ia.get(g) or {}).get(cle)
        if isinstance(propose, str) and propose.strip() and valide(propose):
            resultat[g][cle] = {"texte": propose.strip(), "source": "ia"}
        else:
            resultat[g][cle] = {"texte": fait[0].upper() + fait[1:] + ".", "source": "sans IA"}
            if ia:
                rejets.append(f"{g}/{cle}")
resultat["source"] = {"modele": f"Claude ({MODELE}) via claude -p" if ia else "aucun (texte déterministe)",
                      "faits": "data/gold/kpi.csv et tables Gold"}
(GOLD / "commentaires_ia_filtres.json").write_text(json.dumps(resultat, ensure_ascii=False, indent=1), encoding="utf-8")
total = sum(len(v) for k, v in resultat.items() if k != "source")
n_ia = sum(1 for k, v in resultat.items() if k != "source" for x in v.values() if x["source"] == "ia")
print(f"commentaires_ia_filtres.json : {total} commentaires, {n_ia} rédigés par l'IA et contrôlés"
      + (f" ; remplacés : {rejets}" if rejets else ""))
