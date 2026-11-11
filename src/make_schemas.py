"""Génère les schémas du README : modèle relationnel (Silver) et modèle cible en étoile / flocon (Gold)."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from paths import ROOT

IMAGES = ROOT / "docs" / "images"
IMAGES.mkdir(parents=True, exist_ok=True)

INK, MUTED, SURFACE = "#0b0b0b", "#52514e", "#fcfcfb"
BLUE, ORANGE, GREY, GREEN = "#2a78d6", "#eb6834", "#898781", "#1baf7a"
ROW = 0.36


def table(ax, x, y, title, rows, color, width=3.6):
    """Une table : bandeau titre + une ligne par colonne. rows = [(tag, nom)], tag in {PK, FK, PK FK, ''}."""
    h = ROW * (len(rows) + 1)
    ax.add_patch(FancyBboxPatch((x, y - h), width, h, boxstyle="round,pad=0.02", fc="white", ec=color, lw=1.6))
    ax.add_patch(FancyBboxPatch((x, y - ROW), width, ROW, boxstyle="round,pad=0.02", fc=color, ec=color))
    ax.text(x + width / 2, y - ROW / 2, title, ha="center", va="center", color="white", weight="bold", fontsize=10)
    for i, (tag, name) in enumerate(rows):
        yy = y - ROW * (i + 1.5)
        if tag:
            ax.text(x + 0.1, yy, tag, va="center", fontsize=7.5, weight="bold",
                    color=ORANGE if "FK" in tag and "PK" not in tag else BLUE)
        ax.text(x + 0.75, yy, name, va="center", fontsize=8.5, family="monospace", color=INK)
    return {"l": (x, y - ROW * 1.5), "r": (x + width, y - ROW * 1.5),
            "t": (x + width / 2, y), "b": (x + width / 2, y - h), "x": x, "y": y, "w": width, "h": h}


def link(ax, a, b, label, dashed=False, rad=0.0, offset=(0, 0.15)):
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-", color=GREY, lw=1.4,
                                                    ls="--" if dashed else "-",
                                                    connectionstyle=f"arc3,rad={rad}"))
    ax.text((a[0] + b[0]) / 2 + offset[0], (a[1] + b[1]) / 2 + offset[1], label, ha="center", fontsize=8,
            color=MUTED, bbox=dict(fc=SURFACE, ec="none", pad=1.5))


def canvas(w, h, title, subtitle):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    ax.text(0.3, h - 0.35, title, fontsize=15, weight="bold", color=INK, va="top")
    ax.text(0.3, h - 0.85, subtitle, fontsize=10, color=MUTED, va="top")
    return fig, ax


def legend(ax, x, y, items):
    for i, (color, label) in enumerate(items):
        ax.add_patch(FancyBboxPatch((x, y - i * 0.4 - 0.12), 0.3, 0.24, boxstyle="round,pad=0.01", fc=color, ec=color))
        ax.text(x + 0.45, y - i * 0.4, label, va="center", fontsize=9, color=INK)


# ---------------------------------------------------------------- 1. Modèle relationnel (tables Silver)
fig, ax = canvas(19, 11.5, "Modèle de données relationnel : les tables nettoyées (Silver) et leurs clés",
                 "PK = clé primaire (identifie une ligne de façon unique) · FK = clé étrangère (pointe vers la PK "
                 "d'une autre table) · N : 1 = plusieurs lignes d'un côté pour une seule de l'autre")
corr = table(ax, 7.6, 10.0, "correspondance_categories", [
    ("PK", "categorie_id (TECH / LIVRES)"), ("", "code_marche_eurostat"), ("", "code_prix_eurostat"),
    ("", "correspondance (exacte / approx.)")], GREEN, width=4.2)
marche = table(ax, 0.5, 8.3, "marche  (Eurostat)", [
    ("PK", "pays"), ("PK", "annee"), ("PK FK", "categorie_code"), ("", "depenses_menages_meur"),
    ("", "statut_eurostat")], BLUE)
prix = table(ax, 14.9, 8.3, "prix  (Eurostat)", [
    ("PK", "pays"), ("PK", "annee"), ("PK FK", "categorie_code"), ("", "indice_niveau_prix_ue100"),
    ("", "statut_eurostat")], BLUE)
pop = table(ax, 7.9, 7.4, "population  (Eurostat)", [
    ("PK", "pays"), ("PK", "annee"), ("", "population_1er_janvier"), ("", "statut_eurostat")], BLUE)
sources = table(ax, 7.6, 4.85, "sources_officielles  (rapports)", [
    ("PK", "indicateur"), ("PK", "pays"), ("", "annee"), ("", "valeur, unite"), ("", "source, page, url")],
    ORANGE, width=4.2)
communes = table(ax, 0.5, 4.3, "communes  (Destatis)", [
    ("PK", "code_commune"), ("", "nom"), ("", "land_code, land_nom"), ("", "population, superficie_km2"),
    ("", "longitude, latitude")], BLUE)
magasins = table(ax, 0.5, 1.75, "magasins_concurrents  (sitemaps)", [
    ("PK", "magasin_id"), ("FK", "code_commune"), ("", "enseigne, page, methode_rattachement")],
    BLUE, width=4.6)
hubs = table(ax, 14.9, 2.75, "hubs_logistiques  (Fnac Darty)", [
    ("PK", "code_insee"), ("", "hub, commune"), ("", "longitude, latitude")], ORANGE)

link(ax, marche["r"], (corr["x"], corr["y"] - ROW * 2.5), "categorie_code = code_marche_eurostat   N : 1", rad=-0.1)
link(ax, prix["l"], (corr["x"] + corr["w"], corr["y"] - ROW * 3.5), "categorie_code = code_prix_eurostat   N : 1",
     rad=0.1)
link(ax, (marche["x"] + marche["w"], marche["y"] - ROW * 2.5), (pop["x"], pop["y"] - ROW * 2),
     "pays + annee   N : 1", offset=(0, -0.3))
link(ax, (prix["x"], prix["y"] - ROW * 2.5), (pop["x"] + pop["w"], pop["y"] - ROW * 2),
     "pays + annee   N : 1", offset=(0, -0.3))
link(ax, sources["t"], pop["b"], "pays + annee   N : 1", offset=(1.2, 0))
link(ax, (magasins["x"] + 1.2, magasins["y"]), (communes["x"] + 1.2, communes["b"][1]), "code_commune   N : 1",
     offset=(1.3, 0))
# Ligne horizontale qui passe sous sources_officielles
link(ax, hubs["l"], (communes["x"] + communes["w"], hubs["l"][1]),
     "distance calculée à partir des coordonnées (pas une clé)", dashed=True)
legend(ax, 6.2, 1.3, [(BLUE, "Données téléchargées par script (API, fichiers officiels)"),
                       (ORANGE, "Chiffres relevés dans des rapports officiels"),
                       (GREEN, "Table de correspondance créée par l'équipe")])
fig.savefig(IMAGES / "01_modele_relationnel.png", dpi=150, bbox_inches="tight", facecolor=SURFACE)
plt.close(fig)

# ---------------------------------------------------------------- 2. Modèle cible en étoile / flocon (Gold)
fig, ax = canvas(19, 12, "Modèle cible (Gold) : 4 tables de faits qui partagent leurs dimensions",
                 "Fait = ce qu'on mesure (nombres que l'on additionne) · Dimension = ce qui décrit et sert de filtre "
                 "(texte, date) · dim_commune → dim_land = flocon")
DIM, FACT = "#52514e", BLUE
f_marche = table(ax, 7.4, 10.0, "fact_marche", [
    ("PK FK", "pays_id"), ("PK FK", "annee"), ("PK FK", "categorie_id"), ("", "depenses_menages_meur"),
    ("", "indice_niveau_prix_ue100"), ("", "statut_eurostat")], FACT, width=4.4)
f_pop = table(ax, 7.4, 6.85, "fact_population", [
    ("PK FK", "pays_id"), ("PK FK", "annee"), ("", "population_1er_janvier")], FACT, width=4.4)
f_ind = table(ax, 7.4, 5.0, "fact_indicateurs_officiels", [
    ("PK FK", "indicateur_id"), ("PK FK", "pays_id"), ("FK", "annee"), ("", "valeur")], FACT, width=4.4)
f_mag = table(ax, 7.4, 2.5, "fact_magasins_concurrents", [
    ("PK", "magasin_id"), ("FK", "code_commune"), ("", "nb_magasins (= 1)")], FACT, width=4.4)

d_cat = table(ax, 14.4, 11.0, "dim_categorie", [
    ("PK", "categorie_id"), ("", "categorie_fr"), ("", "code_marche / code_prix"), ("", "correspondance")], DIM,
    width=4.2)
d_pays = table(ax, 0.6, 10.0, "dim_pays", [("PK", "pays_id (DE / FR)"), ("", "nom_pays")], DIM)
d_annee = table(ax, 0.6, 7.6, "dim_annee", [("PK", "annee"), ("", "est_provisoire")], DIM)
d_ind = table(ax, 14.4, 6.6, "dim_indicateur", [
    ("PK", "indicateur_id"), ("", "libelle, unite"), ("", "source, page, url")], DIM, width=4.2)
d_com = table(ax, 0.6, 4.6, "dim_commune", [
    ("PK", "code_commune"), ("", "nom, population"), ("", "longitude, latitude"), ("", "distance_hub_km"),
    ("FK", "land_code")], DIM, width=4.0)
# Sous dim_commune : la dimension rattachée à une autre dimension (le flocon) se lit de haut en bas
d_land = table(ax, 0.6, 1.7, "dim_land  (flocon)", [("PK", "land_code"), ("", "land_nom")], DIM, width=4.0)

link(ax, d_pays["r"], f_marche["l"], "pays_id", offset=(0, 0.12))
link(ax, (d_pays["x"] + d_pays["w"], d_pays["b"][1] + 0.1), f_pop["l"], "pays_id", rad=0.1, offset=(0, -0.35))
link(ax, d_annee["r"], (f_marche["x"], f_marche["y"] - ROW * 2.5), "annee", offset=(0, -0.3))
link(ax, (d_annee["x"] + d_annee["w"], d_annee["b"][1] + 0.1), (f_pop["x"], f_pop["y"] - ROW * 2.5), "annee",
     offset=(0, -0.25))
link(ax, (d_annee["x"] + d_annee["w"], d_annee["b"][1]), (f_ind["x"], f_ind["y"] - ROW * 3.5), "annee",
     rad=0.1, offset=(0, -0.3))
link(ax, (d_pays["x"] + d_pays["w"], d_pays["b"][1] + 0.05), (f_ind["x"], f_ind["y"] - ROW * 2.5), "pays_id",
     rad=-0.12, offset=(0.9, 0.2))
link(ax, (f_marche["x"] + f_marche["w"], f_marche["y"] - ROW * 3.5), d_cat["l"], "categorie_id", offset=(0, 0.1))
link(ax, (f_ind["x"] + f_ind["w"], f_ind["y"] - ROW * 1.5), d_ind["l"], "indicateur_id")
link(ax, f_mag["l"], (d_com["x"] + d_com["w"], d_com["y"] - ROW * 1.5), "code_commune", offset=(0, 0.12))
link(ax, d_com["b"], d_land["t"], "land_code  (flocon : dimension → dimension)", offset=(2.3, 0))
legend(ax, 14.4, 0.9, [(FACT, "Table de faits (mesures)"), (DIM, "Table de dimension (axes d'analyse)")])
fig.savefig(IMAGES / "02_modele_etoile_flocon.png", dpi=150, bbox_inches="tight", facecolor=SURFACE)
plt.close(fig)
print("Schémas :", sorted(p.name for p in IMAGES.glob("*.png")))
