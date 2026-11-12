"""Gold -> docs/slides.html : la présentation de l'oral en page web autonome (12 slides animées, notes de l'oral avec N).

Mêmes données que le dashboard (src/restitution/donnees.py). Les « lectures IA » sont les commentaires rédigés par
Claude (src/ai/commentaires_dashboard.py, claude -p, chiffres contrôlés) ; la phrase qui annonce la décision est retirée,
pour que le Go n'apparaisse qu'en conclusion.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import donnees  # noqa: E402
from paths import GOLD, ROOT  # noqa: E402

HERE = Path(__file__).resolve().parent
data = donnees.donnees()
ia_path = GOLD / "commentaires_ia_filtres.json"
ia = json.loads(ia_path.read_text(encoding="utf-8")) if ia_path.exists() else None


def sans_decision(texte):
    return " ".join(p for p in re.split(r"(?<=\.) ", texte) if "Go" not in p and "pilote" not in p and "Darty" not in p)


lectures = {} if ia is None else {
    "K1": sans_decision(ia["kpi"]["K1"]["texte"]),
    "K12": sans_decision(ia["kpi"]["K12"]["texte"]),
    "Köln": sans_decision(ia["villes"]["Köln"]["texte"]),
}
html = (HERE / "slides_template.html").read_text(encoding="utf-8")
html = html.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False)).replace("/*__IA__*/null", json.dumps(lectures, ensure_ascii=False))
assert "__DATA__" not in html and "__IA__" not in html
(ROOT / "docs" / "slides.html").write_text(html, encoding="utf-8")
print(f"docs/slides.html : {len(html) / 1024:.0f} Ko, 12 slides (9 + 3 annexes)")
