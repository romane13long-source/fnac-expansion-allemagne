"""Gold -> docs/dashboard.html : un fichier HTML autonome (aucune bibliothèque externe).

Seules les DONNÉES sont insérées dans dashboard_template.html. Les commentaires IA ne sont pas
pré-générés : la page les demande à Claude en direct quand elle est ouverte sur claude.ai
(capacité « sample »), à partir des chiffres de l'onglet et des filtres choisis.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import donnees  # noqa: E402
from paths import ROOT  # noqa: E402

HERE = Path(__file__).resolve().parent
data = donnees.donnees()
html = (HERE / "dashboard_template.html").read_text(encoding="utf-8")
pre_path = ROOT / "data" / "gold" / "commentaires_par_filtre.json"  # produit par src/ai/commentaires_par_filtre.py
pre = json.loads(pre_path.read_text(encoding="utf-8")) if pre_path.exists() else {}
pre = {k: v.replace("Köln", "Cologne") for k, v in pre.items()}  # nom français dans les commentaires affichés
html = html.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False)).replace("/*__AI_PRE__*/{}", json.dumps(pre, ensure_ascii=False))
assert "__DATA__" not in html
(ROOT / "docs").mkdir(exist_ok=True)
(ROOT / "docs" / "dashboard.html").write_text(html, encoding="utf-8")
# Version pour la page claude.ai : sans le squelette <html>/<head>/<body> (ajouté à la publication)
import re  # noqa: E402
corps = re.sub(r"(?s)^.*?<head>|</head>\s*<body>|</body>\s*</html>\s*$", "", html)
corps = re.sub(r'<meta charset="utf-8">\s*<meta name="viewport"[^>]*>\s*', "", corps)
(ROOT / "docs" / "dashboard_claude_ai.html").write_text(corps.strip() + "\n", encoding="utf-8")
print(f"docs/dashboard.html : {len(html) / 1024:.0f} Ko, 12 onglets, {len(data['villes'])} villes candidates")
