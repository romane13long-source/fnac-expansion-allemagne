"""Lance le pipeline : collecte (Bronze) puis nettoyage (Silver)."""
import runpy
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(SRC))

STEPS = ["collect/eurostat", "collect/destatis", "clean/eurostat", "clean/destatis", "clean/manual"]

for step in STEPS:
    print(f"\n=== {step}")
    runpy.run_path(str(SRC / f"{step}.py"), run_name="__main__")
