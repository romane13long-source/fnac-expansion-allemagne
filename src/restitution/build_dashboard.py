"""Gold -> docs/dashboard.html : un fichier HTML autonome (aucune bibliothèque externe, marche hors ligne).

Les données (src/restitution/donnees.py) et les commentaires IA par filtre (data/gold/commentaires_ia_filtres.json,
produits par src/ai/commentaires_dashboard.py) sont insérés dans dashboard_template.html.
"""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import donnees  # noqa: E402
from paths import GOLD, ROOT

HERE = Path(__file__).resolve().parent
ia = json.loads((GOLD / "commentaires_ia_filtres.json").read_text(encoding="utf-8"))
data = donnees.donnees()
data["kpi_table"] = donnees.kpi.to_dict("records")


def md_html(md):
    """Synthèse IA (docs/synthese_ia.md) -> HTML simple : titres ###/##, paragraphes, puces. Les [K..] restent (traçabilité)."""
    out, liste = [], False
    for ligne in md.splitlines()[1:]:  # saute le titre « # Synthèse pour le Comex »
        ligne = html.escape(ligne.strip())
        if ligne.startswith("*Générée"):
            continue
        if liste and not ligne.startswith("- "):
            out.append("</ul>"); liste = False
        if ligne.startswith("### ") or ligne.startswith("## "):
            out.append(f"<h3>{ligne.lstrip('# ')}</h3>")
        elif ligne.startswith("- "):
            if not liste:
                out.append("<ul>"); liste = True
            gras = re.sub(r"[*][*](.+?)[*][*]", lambda m: f"<b>{m.group(1)}</b>", ligne[2:])
            out.append(f"<li>{gras}</li>")
        elif ligne:
            out.append(f"<p>{ligne}</p>")
    return "\n".join(out + (["</ul>"] if liste else []))


synthese = (ROOT / "docs" / "synthese_ia.md").read_text(encoding="utf-8")
ia["synthese_html"] = md_html(synthese)
ia["synthese_source"] = re.search(r"Générée par : ([^.]+)", synthese).group(1)
assert set(ia["lands"]) == {x["land"] for x in data["lands"]}, "un Land n'a pas de commentaire IA : relancer commentaires_dashboard.py"

html = (HERE / "dashboard_template.html").read_text(encoding="utf-8")
html = html.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False)).replace("/*__AI__*/null", json.dumps(ia, ensure_ascii=False))
assert "__DATA__" not in html and "__AI__" not in html
(ROOT / "docs").mkdir(exist_ok=True)
(ROOT / "docs" / "dashboard.html").write_text(html, encoding="utf-8")
print(f"docs/dashboard.html : {len(html) / 1024:.0f} Ko, 6 onglets, {len(data['lands'])} Länder")
