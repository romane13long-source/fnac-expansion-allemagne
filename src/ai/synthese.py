"""Brique IA (slide 5, « Commentaires & Synthèse IA ») : rédige la synthèse et les commentaires pour le Comex.

- Entrée : uniquement data/gold/kpi.csv (des chiffres déjà calculés et validés). L'IA ne calcule rien.
- Modèle : Claude, appelé en mode non interactif (`claude -p`, Claude Code), sans aucun outil
  (`--tools ""`) : il ne lit ni fichier ni site, seulement le texte qu'on lui envoie. Aucune clé d'API
  dans le projet : la commande utilise la session Claude Code de la personne qui lance le script.
- Contrôle : toutes les sections attendues sont présentes, et chaque nombre écrit par l'IA existe dans les KPI fournis. Sinon on régénère une fois,
  puis on se replie sur un texte déterministe (même structure, produit sans IA).
- Sorties : docs/synthese_ia.md (texte complet) et data/gold/commentaires_ia.csv (un commentaire par axe,
  pour le dashboard).

Lancement : .venv/bin/python src/ai/synthese.py   (option --sans-ia pour forcer le texte déterministe)
"""
import re
import shutil
import subprocess
import sys

import pandas as pd

from paths import GOLD, ROOT, SILVER

MODELE = "sonnet"  # rédaction : tâche de difficulté moyenne
AXES = ["Marché & Potentiel", "Prix & Marges", "Réseau & Implantation", "Opérations & Logistique", "Assortiment", "Synthèse"]
DECISION = ("Go conditionnel : un magasin pilote à Cologne. Conditions : achats via une centrale allemande "
            "(marge brute proche de 28 %), loyer inférieur au seuil K12_seuil_loyer, assortiment TECH + jeux vidéo. "
            "Décision de déploiement après 2 ans d'exploitation.")

kpi = pd.read_csv(GOLD / "kpi.csv", keep_default_na=False)
LAST = kpi.loc[kpi["kpi_id"].eq("K1a"), "annee"].max()
# On garde les valeurs utiles à la décision : la croissance de la dernière année, l'indice de prix de la dernière année
faits = kpi[~(kpi["kpi_id"].isin(["K1a", "K4_ttc", "K4_ht", "K5"]) & kpi["annee"].ne(LAST))]


def fmt(x):
    return f"{x:.2f}".rstrip("0").rstrip(".").replace(".", ",")


def table_kpi(df):
    lignes = [f"{r.kpi_id} | {r.axe} | {r.kpi} | {r.pays_id} {r.categorie_id} {r.zone}".rstrip() +
              f" | {fmt(r.valeur)} {r.unite} | {r.nature}" for r in df.itertuples()]
    return "\n".join(lignes)


PROMPT = f"""Tu es analyste data. Rédige en français, pour le Comex de la Fnac, la synthèse d'une étude :
« L'implantation de la Fnac en Allemagne est-elle réalisable et rentable ? »

Décision prise par l'équipe : {DECISION}

Règles strictes :
- Utilise UNIQUEMENT les chiffres du tableau ci-dessous, écrits avec une virgule décimale, arrondis à au plus 1 décimale.
- Après chaque chiffre, mets son identifiant entre crochets, par exemple « 17,3 % [K2] ».
- Signale « (estimation) », « (hypothèse) » ou « (simulé) » quand la colonne nature le dit.
- Une valeur 999 années signifie « jamais rentable » : écris « jamais », pas 999.
- N'invente aucun chiffre, aucune source, aucun nom de ville autre que Cologne.

Format exact (Markdown) :
## Synthèse
Trois paragraphes courts : constat, arbitrage, recommandation (150 à 200 mots au total).
## Commentaires par axe
Pour chacun de ces axes, un titre « ### <axe> » puis 2 phrases maximum : {", ".join(AXES)}.
## Risques
Trois puces, puis rien d'autre : aucune remarque, aucune note après les puces.

Tableau des KPI (identifiant | axe | KPI | périmètre | valeur | nature) :
{table_kpi(faits)}
"""


def nombres_autorises():
    """Toutes les valeurs du tableau, arrondies comme l'IA peut les écrire (0, 1 ou 2 décimales)."""
    ok = set()
    for x in kpi["valeur"].abs():  # le signe moins est lu à part : « -0,8 » est contrôlé comme 0,8
        for d in (0, 1, 2):
            ok.add(round(x, d))
        ok.add(round(x))
    ok |= {round(x, 1) for x in kpi["annee"].astype(float)}
    ok |= {0, 1, 2, 3, 28, 100}  # nombres de la consigne : 2 ans, 3 scénarios, 28 % de marge, base 100
    # Hypothèses et chiffres officiels cités dans les libellés des KPI (2 400 m², 1 500 €/m², 115 €/m²…)
    # Nombres écrits dans les libellés envoyés à l'IA (ex. scénario « invest 2000 €/m² »)
    for libelle in pd.concat([faits["kpi"], faits["zone"]]):
        ok |= {float(n.replace(" ", "")) for n in re.findall(r"\d+(?: \d{3})*", libelle)}
    for fichier in (SILVER / "hypotheses_roi.csv", GOLD / "fact_indicateurs_officiels.csv"):
        ok |= {round(float(x), 1) for x in pd.read_csv(fichier)["valeur"]}
    return ok


def nombres_inconnus(texte):
    texte = re.sub(r"\[[^\]]*\]", "", texte)  # retire les identifiants [K12_...]
    texte = re.sub(r"(?<=\d)[  ](?=\d{3}\b)", "", texte)  # 1 500 -> 1500
    inconnus = []
    autorises = nombres_autorises()
    for brut in re.findall(r"\d+(?:,\d+)?", texte):
        valeur = float(brut.replace(",", "."))
        if not any(abs(valeur - a) < 0.051 for a in autorises):
            inconnus.append(brut)
    return inconnus


def couper_apres_risques(texte):
    """Garde le texte jusqu'à la fin des puces « ## Risques » : retire une éventuelle note ajoutée après."""
    debut, _, risques = texte.partition("## Risques")
    puces = []
    for ligne in risques.strip().splitlines():
        if ligne.startswith("- "):
            puces.append(ligne)
        elif puces and ligne.strip():
            break
    return f"{debut}## Risques\n\n" + "\n".join(puces)


def appeler_claude():
    resultat = subprocess.run(
        ["claude", "-p", "--model", MODELE, "--tools", "", "--no-session-persistence", "--output-format", "text",
         # réglages du projet seulement : les hooks personnels de la personne qui lance le script ne s'appliquent pas
         "--setting-sources", "project"],
        input=PROMPT, capture_output=True, text=True, timeout=300)
    if resultat.returncode != 0:
        raise RuntimeError(resultat.stderr.strip()[:300])
    return couper_apres_risques(resultat.stdout.strip())


def texte_deterministe():
    """Repli sans IA : mêmes sections, phrases à trous remplies avec les KPI."""
    def val(kid, zone="", cat="", pays="DE"):  # dernière année disponible (K4 et K5 existent pour 2022 à 2025)
        lignes = kpi[(kpi.kpi_id == kid) & (kpi.zone == zone) & (kpi.categorie_id == cat) & (kpi.pays_id == pays)]
        assert len(lignes), f"KPI introuvable : {kid} {pays} {cat} {zone}"
        return lignes.sort_values("annee")["valeur"].iloc[-1]
    d = "D. achats locaux + loyer niveau France"
    return f"""## Synthèse
Le marché allemand des produits techniques grandit de {fmt(val('K1b', cat='TECH'))} % par an en moyenne [K1b], mais les prix y sont plus bas (indice hors taxes {fmt(val('K4_ht', cat='TECH'))}, France = 100 [K4_ht]) : à coût d'achat français, la marge brute tombe à {fmt(val('K5', cat='TECH'))} % [K5] (estimation).

Seul le scénario achats locaux et loyer modéré est rentable : délai de retour de {fmt(val('K12', zone=d))} ans [K12] (estimation), à condition d'un loyer inférieur à {fmt(val('K12_seuil_loyer'))} €/m²/mois [K12_seuil_loyer].

Recommandation : {DECISION}

## Commentaires par axe
### Marché & Potentiel
CECONOMY détient entre {fmt(val('K3_bas', cat='TECH'))} % et {fmt(val('K3_haut', cat='TECH'))} % du marché TECH [K3] (estimation).
### Prix & Marges
Prix TECH allemands inférieurs aux prix français [K4_ht] : la marge dépend des conditions d'achat.
### Réseau & Implantation
Densité CECONOMY moyenne : {fmt(val('K6', zone='Allemagne'))} magasins par million d'habitants [K6].
### Opérations & Logistique
Distance moyenne depuis le hub : {fmt(val('K8'))} km [K8] ; droits de douane : {fmt(val('K9_douane'))} % [K9_douane].
### Assortiment
{fmt(val('K11'))} % du catalogue est éligible [K11] (simulé).
### Synthèse
Go conditionnel : pilote à Cologne.

## Risques
- Marge écrasée si les achats restent en France [K5].
- Loyer au-dessus du seuil [K12_seuil_loyer].
- Concurrent installé [K3].
"""


def commentaires_par_axe(texte):
    lignes = []
    for axe in AXES:
        bloc = re.search(rf"### {re.escape(axe)}\s*\n(.*?)(?=\n###|\n## |\Z)", texte, re.S)
        lignes.append({"axe": axe, "commentaire": bloc.group(1).strip() if bloc else ""})
    return pd.DataFrame(lignes)


source = "texte déterministe (sans IA)"
texte = None
if "--sans-ia" not in sys.argv and shutil.which("claude"):
    for essai in (1, 2):
        try:
            candidat = appeler_claude()
        except Exception as erreur:  # commande absente, session expirée, délai dépassé
            print(f"essai {essai} : appel à Claude impossible ({erreur})")
            continue
        manquants = [t for t in ["## Synthèse", "## Commentaires par axe", "## Risques"] + [f"### {a}" for a in AXES]
                     if t not in candidat]
        if manquants:
            print(f"essai {essai} : format non respecté, sections manquantes {manquants[:3]} -> rejeté")
            continue
        inconnus = nombres_inconnus(candidat)
        if not inconnus:
            texte, source = candidat, f"Claude ({MODELE}) via claude -p, chiffres contrôlés"
            break
        print(f"essai {essai} : chiffres absents des KPI {inconnus[:8]} -> rejeté")
if texte is None:
    texte = texte_deterministe()
    assert not nombres_inconnus(texte), "le texte de repli contient un chiffre absent des KPI"

entete = (f"# Synthèse pour le Comex\n\n*Générée par : {source}. Source des chiffres : `data/gold/kpi.csv`. "
          "Validation humaine obligatoire avant diffusion.*\n\n")
(ROOT / "docs").mkdir(exist_ok=True)
(ROOT / "docs" / "synthese_ia.md").write_text(entete + texte + "\n", encoding="utf-8")
commentaires = commentaires_par_axe(texte)
commentaires.to_csv(GOLD / "commentaires_ia.csv", index=False)
print(f"docs/synthese_ia.md écrit ({source}) ; commentaires_ia.csv : "
      f"{commentaires['commentaire'].ne('').sum()} axes commentés sur {len(AXES)}")
