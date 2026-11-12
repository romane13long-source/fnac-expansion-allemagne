"""Lance le pipeline : collecte (Bronze), nettoyage (Silver), modèle en étoile (Gold), KPI, dashboard et slides.

La brique IA (src/ai/) se lance à part : elle a besoin de Claude Code (claude -p).
"""
import runpy
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(SRC))

STEPS = ["collect/eurostat", "collect/destatis", "collect/enseignes",
         "clean/eurostat", "clean/destatis", "clean/enseignes", "clean/manual",
         "gold/dimensions", "gold/fact_marche", "gold/facts", "gold/catalogue_simule", "gold/kpi",
         "restitution/build_dashboard", "restitution/build_slides"]

for step in STEPS:
    print(f"\n=== {step}")
    runpy.run_path(str(SRC / f"{step}.py"), run_name="__main__")
