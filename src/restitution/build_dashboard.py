"""Gold -> docs/dashboard.html : un fichier HTML autonome (aucune bibliothèque externe, marche hors ligne).

Les données (src/restitution/donnees.py) et les commentaires IA par filtre (data/gold/commentaires_ia_filtres.json,
produits par src/ai/commentaires_dashboard.py) sont insérés dans dashboard_template.html.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import donnees  # noqa: E402
from paths import GOLD, ROOT

HERE = Path(__file__).resolve().parent
ia = json.loads((GOLD / "commentaires_ia_filtres.json").read_text(encoding="utf-8"))
data = donnees.donnees()
assert set(ia["lands"]) == {x["land"] for x in data["lands"]}, "un Land n'a pas de commentaire IA : relancer commentaires_dashboard.py"

html = (HERE / "dashboard_template.html").read_text(encoding="utf-8")
html = html.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False)).replace("/*__AI__*/null", json.dumps(ia, ensure_ascii=False))
assert "__DATA__" not in html and "__AI__" not in html
(ROOT / "docs").mkdir(exist_ok=True)
(ROOT / "docs" / "dashboard.html").write_text(html, encoding="utf-8")
print(f"docs/dashboard.html : {len(html) / 1024:.0f} Ko, 6 onglets, {len(data['lands'])} Länder")
