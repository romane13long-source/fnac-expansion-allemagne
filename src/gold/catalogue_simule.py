"""Catalogue France SIMULÉ -> % du catalogue éligible en Allemagne (slide 7, axe Assortiment).

DONNÉES SIMULÉES (règle de gestion n° 10) : le catalogue réel de la Fnac n'est pas public.
On génère 10 000 références fictives, avec une graine fixe (résultat reproductible), puis on applique
des règles d'éligibilité explicites. Chaque proportion ci-dessous est une HYPOTHÈSE de l'équipe.

Règles d'éligibilité pour un magasin en Allemagne :
- TECH : éligible, sauf les produits propres au marché français (clavier AZERTY, box d'opérateur français…).
- LIVRES : seuls les livres qui ne sont pas en français sont éligibles. Ils sont vendus au prix fixe allemand
  (Buchpreisbindungsgesetz § 3, gesetze-im-internet.de) : la référence reste éligible, seul le prix change.
- MUSIQUE_VIDEO : éligible si la référence n'est pas uniquement en français (audio ou sous-titres allemands).
- JEUX_VIDEO : éligible si la boîte est multilingue (allemand inclus).
"""
import numpy as np
import pandas as pd

from paths import GOLD

SEED, N_REFS = 42, 10_000

# HYPOTHÈSES : part de chaque famille dans le catalogue, et part des références propres au marché français
FAMILLES = {
    #  famille         categorie_id  part_catalogue  part_specifique_france
    "TECH":          ("TECH",   0.30, 0.08),
    "LIVRES":        ("LIVRES", 0.45, 0.90),
    "MUSIQUE_VIDEO": ("LIVRES", 0.15, 0.60),
    "JEUX_VIDEO":    ("TECH",   0.10, 0.15),
}

rng = np.random.default_rng(SEED)
noms = list(FAMILLES)
familles = rng.choice(noms, size=N_REFS, p=[FAMILLES[f][1] for f in noms])
specifique = rng.random(N_REFS) < np.array([FAMILLES[f][2] for f in familles])

catalogue = pd.DataFrame({
    "reference_id": [f"SIM-{i:05d}" for i in range(N_REFS)],
    "famille": familles,
    "categorie_id": [FAMILLES[f][0] for f in familles],
    "specifique_france": specifique,
})
catalogue["eligible_allemagne"] = ~catalogue["specifique_france"]
catalogue["nature"] = "simulé"
catalogue.to_csv(GOLD / "catalogue_simule.csv", index=False)

print(f"catalogue_simule.csv : {N_REFS} références SIMULÉES, "
      f"{catalogue['eligible_allemagne'].mean():.1%} éligibles en Allemagne")
print((catalogue.groupby("famille")["eligible_allemagne"].mean() * 100).round(1).to_string())
