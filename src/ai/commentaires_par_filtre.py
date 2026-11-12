"""Brique IA (slide 5) : un commentaire rédigé par Claude pour CHAQUE combinaison de filtres de chaque onglet du dashboard.

Pourquoi : le lien public du dashboard n'a pas de clé d'API, Claude ne peut donc pas y être appelé en direct. On fait
rédiger à l'avance, par Claude (`claude -p`), un commentaire pour chaque état possible de la page (109 combinaisons),
à partir exactement des chiffres que l'onglet affiche. Quand on change un filtre, le commentaire change.

Étapes :
1. Chrome sans fenêtre ouvre docs/dashboard.html et liste, pour chaque onglet et chaque combinaison de filtres,
   les chiffres (« faits ») que l'onglet calcule.
2. Claude rédige 2 à 3 phrases par combinaison, par lots de ~28, en 4 appels parallèles.
3. Chaque commentaire est contrôlé : tout nombre écrit doit exister dans les faits de sa combinaison ; sinon il est
   rejeté et l'onglet affichera la phrase calculée sans IA.
Sortie : data/gold/commentaires_par_filtre.json, intégré au dashboard par src/restitution/build_dashboard.py.
Lancement : PYTHONPATH=src .venv/bin/python src/ai/commentaires_par_filtre.py
"""
import html
import json
import re
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from paths import GOLD, ROOT

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
MODELE = "sonnet"
HARNESS = """<script>
setTimeout(() => {
  const VAL = { ville: D.villes.map(v => v.ville), cat: ["TECH", "LIVRES"], achats: ["france", "locaux"], loyer: ["ihk", "france"] };
  const out = {};
  for (const p of PAGES) {
    let combos = [{}];
    for (const f of p.f) combos = combos.flatMap(c => VAL[f].map(v => ({ ...c, [f]: v })));
    for (const c of combos) {
      Object.assign(state, c, { tab: p.id, sim: null });
      const b = BUILDERS[p.id]();
      if (b.facts) out[p.id + "|" + p.f.map(f => state[f]).join("|")] = { page: p.label, q: p.q, facts: b.facts };
    }
  }
  document.body.innerHTML = "<pre id=res></pre>"; document.getElementById("res").textContent = JSON.stringify(out);
}, 300);
</script></body>"""


def combinaisons():
    page = (ROOT / "docs" / "dashboard.html").read_text(encoding="utf-8").replace("</body>", HARNESS, 1)
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "harness.html"
        f.write_text(page, encoding="utf-8")
        dom = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--virtual-time-budget=10000", "--dump-dom", f.as_uri()],
                             capture_output=True, text=True, timeout=120).stdout
    return json.loads(html.unescape(re.search(r'<pre id="res">(.*?)</pre>', dom, re.S).group(1)))


def nombres(texte):
    texte = re.sub(r"(?<=\d)[ \u00a0\u202f](?=\d{3}\b)", "", texte)  # espaces des milliers (dont l'insécable fine)
    return [float(n.replace(",", ".")) for n in re.findall(r"\d+(?:,\d+)?", texte)]


def valide(commentaire, faits):
    ok = {round(x, d) for x in nombres(" ".join(faits) + " 2 3 8 28 100") for d in (0, 1, 2)}
    return all(any(abs(n - a) < 0.051 for a in ok) for n in nombres(commentaire))


CONSIGNE = """Tu commentes un dashboard pour le Comex de la Fnac, qui étudie une implantation en Allemagne.
Pour CHAQUE clé ci-dessous, écris 2 à 3 phrases courtes en français, pour quelqu'un qui ne connaît pas le sujet :
ce que montrent les chiffres et ce que cela implique pour la décision. Le commentaire doit refléter précisément les
filtres de la clé (ville, catégorie, achats, loyer). N'utilise QUE les nombres des faits de la clé, sans en calculer de
nouveaux. Écris « (estimation) », « (hypothèse) » ou « (simulé) » quand le fait le dit. Écris « la Fnac », jamais
« une Fnac » ni « Fnac Darty ». Ne compare jamais avec une ville, un pays ou un chiffre absent des faits de la clé. Pas de titre, pas de liste, pas de guillemets droits.
Réponds UNIQUEMENT avec un objet JSON valide : {"<clé>": "<commentaire>", ...}, avec exactement les mêmes clés.
"""


def rediger(lot):
    entree = {k: {"onglet": v["page"], "question": v["q"], "faits": v["facts"]} for k, v in lot.items()}
    for _ in range(3):
        r = subprocess.run(["claude", "-p", "--model", MODELE, "--tools", "", "--no-session-persistence", "--output-format", "text",
                            "--setting-sources", "project"], input=CONSIGNE + "\n" + json.dumps(entree, ensure_ascii=False, indent=1),
                           capture_output=True, text=True, timeout=900)
        m = re.search(r"\{.*\}", r.stdout, re.S)
        try:
            return json.loads(m.group(0))
        except (AttributeError, json.JSONDecodeError):
            continue
    return {}


combos = combinaisons()
cles = list(combos)
lots = [{k: combos[k] for k in cles[i:i + 28]} for i in range(0, len(cles), 28)]
with ThreadPoolExecutor(len(lots)) as pool:
    reponses = {}
    for r in pool.map(rediger, lots):
        reponses.update(r)
resultat, rejets = {}, []
for k, v in combos.items():
    t = reponses.get(k)
    if isinstance(t, str) and t.strip() and valide(t, v["facts"]) and "Darty" not in t:
        resultat[k] = t.strip()
    else:
        rejets.append(k)
(GOLD / "commentaires_par_filtre.json").write_text(json.dumps(resultat, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"commentaires_par_filtre.json : {len(resultat)} / {len(combos)} combinaisons commentées par Claude"
      + (f" ; rejetés ou manquants : {rejets}" if rejets else ""))
