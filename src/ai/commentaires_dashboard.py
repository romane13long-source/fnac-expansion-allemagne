"""Brique IA (slide 5) : un commentaire par valeur de filtre du dashboard, rédigé par Claude (`claude -p`).

Le dashboard change de commentaire quand on change un filtre :
- catégorie (TECH / LIVRES) × axe du guide des KPI (slide 7) -> 10 commentaires ;
- scénario du ROI (A, B, C, D) -> 4 commentaires ;
- Land (16 zones de chalandise) -> 16 commentaires.
Les 30 commentaires sont générés en UN appel, au moment du build (pas pendant la présentation : rien ne
dépend d'internet à l'oral). Chaque commentaire est contrôlé : tout nombre écrit doit figurer dans les faits
envoyés à l'IA. Un commentaire rejeté est remplacé par une phrase déterministe (signalée « sans IA »).

Sortie : data/gold/commentaires_ia_filtres.json
Lancement : PYTHONPATH=src .venv/bin/python src/ai/commentaires_dashboard.py [--sans-ia]
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "restitution"))
import donnees  # noqa: E402

from paths import GOLD  # noqa: E402

MODELE = "sonnet"
AXES = ["Marché & Potentiel", "Prix & Marges", "Réseau & Implantation", "Opérations & Logistique", "Assortiment"]
D = donnees.donnees()
L = D["last"]


def f(x, d=1):
    s = f"{x:,.{d}f}".replace(",", " ").replace(".", ",")
    return s[:-2] if s.endswith(",0") else s


# ------------------------------------------------------------------ faits envoyés à l'IA (et seuls nombres permis)
def faits_categorie(cat):
    c = D["categories"][cat]
    return [
        f"Croissance annuelle moyenne 2015-{L} des dépenses : Allemagne {f(c['croissance_moy']['DE'])} %, France {f(c['croissance_moy']['FR'])} %",
        f"Croissance {L} : Allemagne {f(c['croissance_last']['DE'])} %, France {f(c['croissance_last']['FR'])} %",
        f"Dépenses des ménages {L} : Allemagne {f(c['depenses']['DE'][L], 0)} M€, France {f(c['depenses']['FR'][L], 0)} M€",
        f"Part de marché Fnac Darty en France (HT/HT, estimation, TECH + LIVRES) : {f(D['parts']['fnac_fr'])} %",
        f"Part de marché CECONOMY en Allemagne sur TECH (estimation) : {f(D['parts']['cec_bas'])} à {f(D['parts']['cec_haut'])} %",
        f"Indice de prix hors taxes Allemagne/France {L} (France = 100) : {f(c['indice_ht'][L])}",
        f"Marge brute estimée en Allemagne à coût d'achat français {L} : {f(c['marge'][L])} % (groupe : 28 %)",
        f"Densité CECONOMY moyenne : {f(D['densite_de'])} magasins par million d'habitants ; pression nationale tous réseaux : {f(D['pression_nationale'])}",
        f"Loyer de référence IHK : {f(D['loyer_m2_mois'], 0)} €/m²/mois (hypothèse)",
        f"Distance moyenne pondérée depuis le hub de Chilly-Mazarin : {f(D['distance_moy'], 0)} km ; droits de douane : 0 % ; écart de TVA DE - FR : {f(c['tva']['DE'])} point",
        f"Dépense par habitant {L} : Allemagne {f(c['par_hab']['DE'], 0)} €, France {f(c['par_hab']['FR'], 0)} € ; pénétration {f(c['penetration'], 0)} (France = 100)",
        f"Part du catalogue éligible (simulé) : total {f(D['eligible'])} % ; " +
        ", ".join(f"{k} {f(v)} %" for k, v in D["eligible_familles"].items()),
    ]


def faits_scenarios():
    return [f"{s['nom']} : résultat annuel {f(s['resultat'], 2)} M€ ; délai de retour " +
            ("jamais" if s["delai"] >= 999 else f"{f(s['delai'])} ans") for s in D["scenarios"].values()] + [
        f"Seuil de loyer pour être rentable avec achats locaux : {f(D['seuil_loyer'])} €/m²/mois",
        f"Investissement d'ouverture : {f(D['simu']['invest_m2'] * D['simu']['surface'] / 1e6)} M€ (hypothèse)"]


def faits_lands():
    return [f"{x['land']} : {f(x['densite'])} magasins CECONOMY par million d'habitants ({x['magasins']} magasins, "
            f"{f(x['population'] / 1e6)} M habitants) ; plus grande ville {x['ville']} ({f(x['ville_pop'] / 1e6, 2)} M hab.) "
            f"à {f(x['ville_km'], 0)} km du hub" for x in D["lands"]]


FAITS = {"categorie": {c: faits_categorie(c) for c in ("TECH", "LIVRES")},
         "scenarios": faits_scenarios(), "lands": faits_lands()}
TOUT = json.dumps(FAITS, ensure_ascii=False)


def nombres(texte):
    texte = re.sub(r"(?<=\d)[  ](?=\d{3}\b)", "", texte)
    return [float(n.replace(",", ".")) for n in re.findall(r"\d+(?:,\d+)?", texte)]


AUTORISES = {round(x, d) for x in nombres(TOUT) for d in (0, 1, 2)} | {0, 1, 2, 3, 4, 100, 2027, 2029}


def valide(texte):
    return all(any(abs(n - a) < 0.051 for a in AUTORISES) for n in nombres(texte))


PROMPT = f"""Tu rédiges les commentaires d'un dashboard pour le Comex de la Fnac, qui étudie une implantation en Allemagne.
Décision de l'équipe : Go conditionnel, un magasin pilote à Cologne (Nordrhein-Westfalen), achats via une centrale allemande,
loyer sous le seuil, assortiment produits techniques + jeux vidéo, décision de déploiement après 2 ans.

Règles : français, phrases courtes, 2 phrases maximum par commentaire, ton factuel pour des décideurs.
N'utilise QUE les nombres des faits ci-dessous (virgule décimale). Écris « (estimation) », « (hypothèse) » ou « (simulé) »
quand le fait le dit. Chaque commentaire dit ce que le chiffre implique pour la décision.

Réponds UNIQUEMENT avec un objet JSON valide, sans texte autour, de cette forme :
{{"axes": {{"TECH": {{<axe>: <commentaire>, ...}}, "LIVRES": {{...}}}},
  "scenarios": {{"A": ..., "B": ..., "C": ..., "D": ...}},
  "lands": {{<nom du Land>: <commentaire>, ...}}}}
Axes attendus : {", ".join(AXES)}. Lands attendus : {", ".join(x['land'] for x in D['lands'])}.
Pour chaque Land, dis s'il est plus ou moins favorable qu'un autre pour un magasin (densité concurrente, distance au hub).

Faits :
{json.dumps(FAITS, ensure_ascii=False, indent=1)}
"""


def repli():
    """Phrases sans IA (mêmes clés), utilisées si l'IA échoue ou si un commentaire est rejeté."""
    out = {"axes": {}, "scenarios": {}, "lands": {}}
    for cat in ("TECH", "LIVRES"):
        fa = FAITS["categorie"][cat]
        out["axes"][cat] = {"Marché & Potentiel": fa[0] + ".", "Prix & Marges": fa[5] + " ; " + fa[6] + ".",
                            "Réseau & Implantation": fa[7] + ".", "Opérations & Logistique": fa[9] + ".",
                            "Assortiment": fa[10] + "."}
    for k, phrase in zip("ABCD", FAITS["scenarios"]):
        out["scenarios"][k] = phrase + "."
    for x, phrase in zip(D["lands"], FAITS["lands"]):
        out["lands"][x["land"]] = phrase + "."
    return out


def appeler_claude():
    r = subprocess.run(["claude", "-p", "--model", MODELE, "--tools", "", "--no-session-persistence",
                        "--output-format", "text", "--setting-sources", "project"],
                       input=PROMPT, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:300])
    m = re.search(r"\{.*\}", r.stdout, re.S)
    if not m:
        raise ValueError("pas de JSON dans la réponse")
    return json.loads(m.group(0))


base = repli()
resultat = {"source": {}, **{k: {} for k in base}}
ia = None
if "--sans-ia" not in sys.argv and shutil.which("claude"):
    try:
        ia = appeler_claude()
    except Exception as e:
        print(f"appel à Claude impossible : {e}")


def fusion(chemin, defaut, propose):
    """Garde le texte IA s'il est présent et contrôlé, sinon la phrase déterministe."""
    if isinstance(propose, str) and propose.strip() and valide(propose):
        return propose.strip(), "ia"
    return defaut, "sans IA"


rejets = []
for cat, axes in base["axes"].items():
    resultat["axes"][cat] = {}
    for axe, defaut in axes.items():
        propose = (((ia or {}).get("axes") or {}).get(cat) or {}).get(axe)
        txt, src = fusion(("axes", cat, axe), defaut, propose)
        resultat["axes"][cat][axe] = {"texte": txt, "source": src}
        if ia and src != "ia":
            rejets.append(f"{cat}/{axe}")
for groupe in ("scenarios", "lands"):
    for cle, defaut in base[groupe].items():
        propose = ((ia or {}).get(groupe) or {}).get(cle)
        txt, src = fusion((groupe, cle), defaut, propose)
        resultat[groupe][cle] = {"texte": txt, "source": src}
        if ia and src != "ia":
            rejets.append(f"{groupe}/{cle}")

resultat["source"] = {"modele": f"Claude ({MODELE}) via claude -p" if ia else "aucun (texte déterministe)",
                      "faits": "data/gold/kpi.csv et tables Gold"}
(GOLD / "commentaires_ia_filtres.json").write_text(json.dumps(resultat, ensure_ascii=False, indent=1), encoding="utf-8")
n = sum(1 for g in ("scenarios", "lands") for v in resultat[g].values()) + sum(len(a) for a in resultat["axes"].values())
n_ia = sum(1 for g in ("scenarios", "lands") for v in resultat[g].values() if v["source"] == "ia") + \
    sum(1 for a in resultat["axes"].values() for v in a.values() if v["source"] == "ia")
print(f"commentaires_ia_filtres.json : {n} commentaires, {n_ia} rédigés par l'IA et contrôlés"
      + (f" ; rejetés (remplacés) : {rejets}" if rejets else ""))
