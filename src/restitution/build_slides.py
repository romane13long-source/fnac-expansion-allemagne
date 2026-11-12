"""Gold -> docs/Comex_Fnac_Allemagne.pptx (11 slides, graphiques natifs) + docs/script_oral.md (ce qu'on dit, minuté).

Les slides suivent les 5 sections de l'oral imposées par le sujet (slide 8 du PDF « Data Analytics Project ») :
1. entreprise & pays (1 min) · 2. base de données & cadrage (1 min 30) · 3. pourquoi ces KPI (2 min)
· 4. analyse des chiffres + brique IA (3 min) · 5. Go / No-Go (1 min 30). Même contenu que le dashboard (src/restitution/donnees.py).
Fond blanc partout ; la décision n'apparaît qu'à la conclusion.
"""
import json
import re
import sys
from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION, XL_TICK_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml import parse_xml
from pptx.util import Inches, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))
import donnees  # noqa: E402
from paths import GOLD, ROOT  # noqa: E402

D = donnees.donnees()
ia_path = GOLD / "commentaires_ia_filtres.json"  # généré localement par src/ai/commentaires_dashboard.py (claude -p)
AI = json.loads(ia_path.read_text(encoding="utf-8")) if ia_path.exists() else None
L = D["last"]
T = D["categories"]["TECH"]
SD = D["scenarios"]["D"]
F = D["finances"]
KOLN = next(v for v in D["villes"] if v["ville"] == "Köln")
PDV = {k["enseigne"]: k["pdv"] for k in D["concurrents"]}

# Mise en page de la v2 de l'équipe, couleurs du dashboard : bleu = Allemagne, orange = France, vert / rouge = bon / mauvais
INK, WHITE = RGBColor(0x11, 0x11, 0x11), RGBColor(0xFF, 0xFF, 0xFF)
BLUE, ORANGE = RGBColor(0x2A, 0x78, 0xD6), RGBColor(0xEB, 0x68, 0x34)
GREEN, RED, VIOLET = RGBColor(0x0C, 0x9A, 0x0C), RGBColor(0xD0, 0x3B, 0x3B), RGBColor(0x62, 0x50, 0xD6)
YEL, CREAM = BLUE, RGBColor(0xF4, 0xF4, 0xF1)  # accent = bleu du dashboard ; tuiles gris clair du dashboard
GREY, MUTED, LINE = RGBColor(0xA3, 0xA2, 0x9C), RGBColor(0x52, 0x51, 0x4E), RGBColor(0xE1, 0xE0, 0xD9)
TINT, VTINT, DARKBAR = CREAM, RGBColor(0xF1, 0xEF, 0xFC), INK
FONT = "Arial"


def n(v, d=1):
    s = f"{v:,.{d}f}".replace(",", " ").replace(".", ",")
    return s[:-2] if d and s.endswith(",0") else s


def sg(v, d=1):
    return ("+" if v > 0 else "−" if v < 0 else "") + n(abs(v), d)


prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
M = Inches(0.6)
CW = prs.slide_width - 2 * M
SCRIPT = []


def tb(slide, x, y, w, h, runs, size=16, color=INK, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    box_ = slide.shapes.add_textbox(x, y, w, h)
    tf = box_.text_frame
    tf.word_wrap, tf.vertical_anchor = True, anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    paras = [[(runs, {})]] if isinstance(runs, str) else runs
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment, p.space_after = align, Pt(6)
        for txt, o in para:
            r = p.add_run()
            r.text = txt
            r.font.name, r.font.size = FONT, Pt(o.get("size", size))
            r.font.bold, r.font.color.rgb = o.get("bold", bold), o.get("color", color)
    return box_


def bar(s, x, y, w, h, color=YEL):
    shp = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def slide(section, title, cover=False):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = WHITE
    if cover:  # couverture et conclusion : bande jaune à gauche
        bar(s, 0, 0, Inches(0.13), prs.slide_height)
    tb(s, M, Inches(0.38), CW, Inches(0.3), section.upper(), size=11, bold=True, color=MUTED)
    if title:
        tb(s, M, Inches(0.68), CW, Inches(1.1), title, size=28, bold=True, anchor=MSO_ANCHOR.TOP)
        bar(s, M, Inches(1.72), Inches(0.75), Inches(0.06))
    num = len(prs.slides)
    tb(s, M, Inches(7.05), Inches(6), Inches(0.25), "Fnac → Allemagne · Comex 2027-2029", size=9, color=MUTED)
    tb(s, prs.slide_width - M - Inches(1), Inches(7.05), Inches(1), Inches(0.25), f"{num:02d}", size=10, bold=True, color=MUTED, align=PP_ALIGN.RIGHT)
    return s


def box(s, x, y, w, h, fill):
    shp = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    shp.adjustments[0] = 0.06
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def stat(s, x, y, w, value, label, color=INK, h=Inches(1.55), size=34):
    """Tuile chiffre (modèle v2) : fond crème, barre jaune, gros nombre + ce qu'il mesure, en clair."""
    box(s, x, y, w, h, CREAM)
    bar(s, x, y + Inches(0.08), Inches(0.07), h - Inches(0.16))
    tb(s, x + Inches(0.28), y + Inches(0.12), w - Inches(0.48), Inches(0.75), value, size=size, bold=True, color=color)
    tb(s, x + Inches(0.28), y + Inches(0.82), w - Inches(0.48), h - Inches(0.87), label, size=12, color=MUTED)


def footer(s, txt):
    tb(s, M, Inches(6.78), CW, Inches(0.25), "Source : " + txt, size=9, color=MUTED)


def notes(s, minutage, qui, texte):
    """Notes de présentation (mode présentateur) + même texte dans docs/script_oral.md."""
    s.notes_slide.notes_text_frame.text = f"[{minutage} · {qui}]\n{texte}"
    titre = list(s.shapes)[1].text_frame.text
    SCRIPT.append((len(prs.slides), titre, minutage, qui, texte))


def sans_decision(texte):
    """La décision n'apparaît qu'à la conclusion : on retire les phrases qui l'annoncent."""
    # on retire la phrase entière (jusqu'au point), jamais un morceau de phrase
    return " ".join(p for p in re.split(r"(?<=\.) ", texte) if "Go" not in p and "pilote" not in p)


def lecture_ia(s, x, y, w, groupe, cle, h=Inches(1.0)):
    """Encadré « Lecture IA » : commentaire rédigé par Claude (claude -p) à partir des KPI, chiffres contrôlés."""
    if not AI:
        return
    b = box(s, x, y, w, h, VTINT)
    b.line.fill.background()
    bar(s, x, y + Inches(0.08), Inches(0.07), h - Inches(0.16), VIOLET)
    tb(s, x + Inches(0.28), y + Inches(0.08), w - Inches(0.45), h - Inches(0.12), [
        [("✦ LECTURE IA", {"bold": True, "size": 11, "color": VIOLET}), ("  · rédigée par Claude à partir de nos KPI, chiffres vérifiés", {"size": 9, "color": MUTED})],
        [(sans_decision(AI[groupe][cle]["texte"]), {"size": 12})]], size=12)


def style(chart, legend=False):
    chart.font.name, chart.font.size = FONT, Pt(15)
    chart.has_legend = legend
    if legend:
        chart.legend.position, chart.legend.include_in_layout = XL_LEGEND_POSITION.TOP, False
    chart.value_axis.has_major_gridlines = False
    chart.value_axis.tick_labels.font.size = Pt(13)


def table(s, x, y, w, rows, widths, size=13, header_fill=DARKBAR, h=None):
    tbl = s.shapes.add_table(len(rows), len(rows[0]), x, y, w, h or Inches(0.4 * len(rows))).table
    for j, wd in enumerate(widths):
        tbl.columns[j].width = wd
    for i, r in enumerate(rows):
        for j, v in enumerate(r):
            c = tbl.cell(i, j)
            c.text = str(v)
            c.fill.solid()
            c.fill.fore_color.rgb = header_fill if i == 0 else (TINT if i % 2 else WHITE)
            for p in c.text_frame.paragraphs:
                for run in p.runs:
                    run.font.name, run.font.size = FONT, Pt(size)
                    run.font.bold = i == 0
                    run.font.color.rgb = WHITE if i == 0 else INK
    return tbl


# ============================================================ 1. ENTREPRISE & PAYS (1 min)
s = slide("Comex Fnac · Stratégie 2027-2029", "", cover=True)
tb(s, M, Inches(1.5), CW, Inches(1.2), "Fnac → Allemagne", size=60, bold=True)
tb(s, M, Inches(3.0), Inches(9), Inches(1.0), "L'implantation dans le pays ciblé est-elle réalisable et rentable ?", size=26)
bar(s, M, Inches(4.45), Inches(2.3), Inches(0.07))
tb(s, M, Inches(4.75), CW, Inches(0.4), "Romane LONG · Elena KERVENNIC · Arquam EL MEZOUARI EL GLAOUI · Samantha ASDRUBAL", size=15)
tb(s, M, Inches(5.25), CW, Inches(0.4), "Projet final Data Analytics · Eugenia School M2", size=13, color=MUTED)
footer(s, "projet final Data Analytics, Eugenia School M2 · données publiques, aucune donnée interne réelle de la Fnac")
notes(s, "0:00 → 0:15", "Romane", "Bonjour. Le Comex de la Fnac nous pose une seule question : l'implantation en Allemagne est-elle "
      "réalisable et rentable ? On a construit toute la chaîne de données pour y répondre ; notre décision arrive à la fin.")

s = slide("1 · L'entreprise et le pays cible", "Une Fnac qui rétrécit en France, un marché allemand qui grandit")
w3 = (CW - Inches(0.5)) / 3
stat(s, M, Inches(2.0), w3, f"{D['x_magasins_fr']}", "magasins Fnac en France fin 2025 (1 ouverture, 15 fermetures dans l'année)")
stat(s, M + w3 + Inches(0.25), Inches(2.0), w3, sg(T["croissance_moy"]["DE"]) + " %/an",
     f"croissance des dépenses tech en Allemagne 2015-{L} (France : {sg(T['croissance_moy']['FR'])} %/an)", color=GREEN)
stat(s, M + 2 * (w3 + Inches(0.25)), Inches(2.0), w3, "0", "magasin Fnac en Allemagne, 1er marché d'Europe (83,6 M habitants)", color=BLUE)
tb(s, M, Inches(4.0), CW, Inches(2.6), [
    [("Périmètre : ", {"bold": True}), ("l'enseigne Fnac (biens culturels, produits techniques, services).", {})],
    [("Pourquoi l'Allemagne : ", {"bold": True}), ("le plus grand marché d'Europe, où la Fnac n'a aucun magasin, et son leader MediaMarkt / Saturn est déjà notre concurrent direct.", {})],
    [("Enjeu 2027-2029 : ", {"bold": True}), ("trouver de la croissance hors de France sans détruire de valeur.", {})]], size=18)
footer(s, "Document d'enregistrement universel 2025 p. 39 ; Eurostat nama_10_cp18 et demo_pjan")
notes(s, "0:15 → 1:00", "Romane", f"La Fnac compte {D['x_magasins_fr']} magasins en France fin 2025, après 15 fermetures. Les dépenses "
      f"des ménages allemands en tech progressent de {n(T['croissance_moy']['DE'])} % par an depuis 2015, quand elles reculent de "
      f"{n(abs(T['croissance_moy']['FR']))} % en France. L'Allemagne est le premier marché d'Europe et le groupe n'y a aucun magasin.")

# ============================================================ 2. BASE DE DONNÉES & CADRAGE (1 min 30)
s = slide("2 · Base de données et cadrage · modélisation 20 pts + sources 15 pts", "Un pipeline simple, des sources officielles,\ndes chiffres traçables")
cw3 = (CW - Inches(0.5)) / 3
cartes = [
    ("PIPELINE REPRODUCTIBLE", "Bronze → Silver → Gold", ["Un seul script (run_pipeline.py) enchaîne collecte, nettoyage, modèle et KPI.", "Relancé deux fois : résultat identique.", "Le détail du modèle de données est dans le README."]),
    ("COMMENT ON A COLLECTÉ", "Une source par sujet", ["API Eurostat (office statistique de l'UE) : marché, prix, population", "Destatis : 10 753 communes allemandes", "Scraping des plans de site MediaMarkt / Saturn : 394 magasins", "Rapports annuels (Fnac, CECONOMY), textes de loi (TVA, douane)"]),
    ("CHAQUE CHIFFRE EST ÉTIQUETÉ", "Mesuré, estimation, hypothèse ou simulé", ["mesuré : chiffre officiel", "estimation : notre calcul", "hypothèse : non sourcé", "simulé : données fictives (catalogue)"]),
]
for i, (lab, titre, points) in enumerate(cartes):
    x = M + i * (cw3 + Inches(0.25))
    box(s, x, Inches(2.0), cw3, Inches(4.5), CREAM)
    tb(s, x + Inches(0.3), Inches(2.2), cw3 - Inches(0.6), Inches(0.3), lab, size=11, bold=True, color=MUTED)
    tb(s, x + Inches(0.3), Inches(2.6), cw3 - Inches(0.6), Inches(0.9), titre, size=20, bold=True)
    tb(s, x + Inches(0.3), Inches(3.6), cw3 - Inches(0.6), Inches(2.8), [[("•  " + p_, {})] for p_ in points], size=14)
footer(s, "README § 2 (dictionnaire, règles de gestion) et § 3 (sources) · run_pipeline.py")
notes(s, "1:00 → 2:30", "Elena", "Aucune donnée n'était fournie : tout vient de sources publiques. On a utilisé l'API d'Eurostat, l'office "
      "statistique de l'Union européenne, pour le marché, les prix et la population ; le fichier officiel allemand des communes ; "
      "et du scraping pour localiser les magasins MediaMarkt et Saturn, à partir des plans de site publiés pour les robots. "
      "Le pipeline suit les trois couches du cours : Bronze, Silver, Gold ; le modèle de données est détaillé dans le README. "
      "Chaque chiffre porte son étiquette : mesuré, estimation, hypothèse ou simulé.")

# ============================================================ 3. POURQUOI CES KPI (2 min)
s = slide("3 · La démarche analytique · choix des KPI 30 pts", "Un KPI par question du Comex, un KPI de synthèse pour trancher")
rows = [("Axe du guide", "KPI retenus", "Décision éclairée"),
        ("Marché & potentiel", "Croissance · dépense par habitant · parts de marché Fnac et CECONOMY", "Quel plafond de CA ?"),
        ("Prix & marges", "Niveau de prix DE / FR · marge brute post-taxe", "Notre prix tient-il ?"),
        ("Réseau & implantation", "Densité concurrentielle · coût au m² · 7 villes candidates", "Où ouvrir, à quel coût ?"),
        ("Opérations & logistique", "Distance au hub · douane et TVA", "Livrer depuis la France ?"),
        ("Assortiment", "Pénétration · % du catalogue éligible", "Tout le catalogue ou ciblé ?"),
        ("★ Synthèse", "Délai de retour d'un magasin · cash-flow du groupe", "Go ou No-Go ?")]
table(s, M, Inches(1.95), CW, rows, [Inches(3.0), Inches(5.9), CW - Inches(8.9)], size=15, h=Inches(4.6))
footer(s, "guide des KPI du sujet (slide 7) · définitions et formules : dashboard, onglet « Définitions des KPI », et README § 2.1")
notes(s, "2:30 → 4:30", "Romane", "On a suivi le guide des KPI du Comex, axe par axe, en se demandant pour chacun quelle décision il "
      "éclaire. Aucun ne répond seul à « rentable ? » : on a donc ajouté un KPI de synthèse, le délai de retour d'un magasin, et "
      "le cash-flow du groupe pour savoir s'il peut financer le projet. Méthode : on compare toujours hors taxes, et chaque KPI "
      "a sa définition en clair dans le dashboard.")

# ============================================================ 4. ANALYSE (3 min)
ph = D["par_hab_annees"]["TECH"]
yrs = sorted(ph["DE"])
s = slide("4 · L'analyse · impact décisionnel & dataviz 35 pts", f"Un Allemand dépense {n(ph['DE'][L] / ph['FR'][L], 1)} fois plus en tech qu'un Français")
cd = CategoryChartData()
cd.categories = [str(y) for y in yrs]
cd.add_series("Allemagne", [round(ph["DE"][y]) for y in yrs])
cd.add_series("France", [round(ph["FR"][y]) for y in yrs])
ch = s.shapes.add_chart(XL_CHART_TYPE.LINE, M, Inches(1.85), Inches(7.4), Inches(3.9), cd).chart
style(ch, legend=True)
for ser, col in zip(ch.series, (BLUE, ORANGE)):
    ser.format.line.color.rgb, ser.format.line.width, ser.smooth = col, Pt(4.5), False
ch.has_title = True
ch.chart_title.text_frame.text = "Dépense tech par habitant (€ par an)"
ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(16)
lecture_ia(s, M, Inches(5.85), Inches(7.4), "kpi", "K1")
xs, ws = M + Inches(7.7), prs.slide_width - M - (M + Inches(7.7))
p24 = D["cec_ventes"][2024] / D["marche_tech_ht"][2024] * 100
p25 = D["cec_ventes"][2025] / D["marche_tech_ht"][2025] * 100
stat(s, xs, Inches(1.85), ws, f"{n(ph['DE'][L], 0)} €", f"par habitant et par an en Allemagne ({L}), contre {n(ph['FR'][L], 0)} € en France : dépenses du pays ÷ habitants")
stat(s, xs, Inches(3.55), ws, f"{n(D['parts']['cec_bas'], 0)}–{n(D['parts']['cec_haut'], 0)} %", f"du marché tech tenu par CECONOMY (MediaMarkt + Saturn), stable : {n(p24, 1)} % → {n(p25, 1)} % (estimation)", color=RED)
stat(s, xs, Inches(5.25), ws, "3 réseaux", f"CECONOMY {PDV['MediaMarkt + Saturn']} magasins · Expert > {PDV['Expert']} · Euronics > {n(PDV['Euronics'], 0)} points de vente (+ Otto en ligne)", size=28)
footer(s, "Eurostat nama_10_cp18 ÷ demo_pjan ; CECONOMY Annual Report 2024/25 p. 39 et 109 ; sites officiels d'Expert et d'Euronics (consultés le 12/11/2026)")
notes(s, "4:30 → 5:15", "Elena", f"Premier constat : le marché attire. Un Allemand dépense {n(ph['DE'][L], 0)} euros par an en tech, un "
      f"Français {n(ph['FR'][L], 0)}, et l'écart se creuse depuis 2015. Mais la place est prise : CECONOMY, c'est-à-dire MediaMarkt "
      f"et Saturn, tient entre {n(D['parts']['cec_bas'], 0)} et {n(D['parts']['cec_haut'], 0)} % du marché, et deux coopératives, "
      "Expert et Euronics, ont des centaines de petits magasins.")

pu = D["prix_ue"]["TECH"]
s = slide("4 · L'analyse", "Mais la France est plus chère : vendre au prix allemand écrase la marge")
cd = CategoryChartData()
cd.categories = ["France", "Allemagne"]
cd.add_series(f"Niveau des prix tech {L} (moyenne UE = 100)", [pu["FR"][L], pu["DE"][L]])
ch = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, M, Inches(1.85), Inches(6.4), Inches(1.9), cd).chart
style(ch)
pl = ch.plots[0]
pl.gap_width, pl.has_data_labels = 40, True
pl.data_labels.number_format, pl.data_labels.number_format_is_linked = "0.0", False
pl.data_labels.font.size = Pt(16)
for i, col in enumerate((ORANGE, BLUE)):
    pt = ch.series[0].points[i]
    pt.format.fill.solid()
    pt.format.fill.fore_color.rgb = col
ch.has_title = True
ch.chart_title.text_frame.text = f"Niveau des prix tech {L} (moyenne UE = 100)"
ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(15)
cd = CategoryChartData()
my = sorted(T["marge"])
cd.categories = [str(y) for y in my]
cd.add_series("Marge brute à coût d'achat français (%)", [round(T["marge"][y], 1) for y in my])
ch = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, M, Inches(3.85), Inches(6.4), Inches(2.0), cd).chart
style(ch)
pl = ch.plots[0]
pl.gap_width, pl.has_data_labels = 60, True
pl.data_labels.number_format, pl.data_labels.number_format_is_linked = '0.0" %"', False
pl.data_labels.position, pl.data_labels.font.size = XL_LABEL_POSITION.OUTSIDE_END, Pt(16)
ch.series[0].format.fill.solid()
ch.series[0].format.fill.fore_color.rgb = RED
ch.value_axis.maximum_scale, ch.value_axis.minimum_scale = 30, 0
ch.has_title = True
ch.chart_title.text_frame.text = "Marge brute si l'on achète en France (groupe : 28 %)"
ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(15)
lecture_ia(s, M, Inches(5.95), Inches(6.4), "kpi", "K5", h=Inches(0.55)) if False else None
xs, ws = M + Inches(6.7), prs.slide_width - M - (M + Inches(6.7))
stat(s, xs, Inches(1.85), ws, f"{sg(T['indice_ht'][L] - 100, 0)} %", "prix tech allemands par rapport aux français, hors taxes : la Fnac devra vendre moins cher", color=RED)
stat(s, xs, Inches(3.55), ws, f"{n(T['marge'][L])} %", "de marge brute si on achète au prix français et revend au prix allemand, contre 28 % pour le groupe", color=RED)
stat(s, xs, Inches(5.25), ws, "0 %", "de droits de douane : France et Allemagne sont dans l'union douanière de l'UE ; seule la TVA change (19 % contre 20 %)", color=GREEN)
tb(s, M, Inches(6.0), Inches(6.4), Inches(0.6), f"Formule : 1 − (1 − 28 %) ÷ (indice HT ÷ 100). Exemple {L} : 1 − 0,72 ÷ {n(T['indice_ht'][L] / 100, 4)} = {n(T['marge'][L])} %. La marge de 28 % avec achats locaux est une hypothèse, pas une marge observée.", size=10, color=MUTED)
footer(s, "Eurostat prc_ppp_ind_1 ; Document d'enregistrement universel 2025 p. 30 (marge 28 %) ; EUR-Lex TFUE art. 28 et 30 ; Commission européenne (TVA)")
notes(s, "5:15 → 6:00", "Romane", f"Deuxième constat, et c'est la réponse à une question qu'on nous pose souvent : non, la France n'est pas "
      f"moins chère. Les produits tech y coûtent {n(pu['FR'][L], 1)} contre {n(pu['DE'][L], 1)} en Allemagne, sur une base 100 "
      f"européenne. Si la Fnac achète au prix français et vend au prix allemand, sa marge tombe à {n(T['marge'][L])} %, contre 28 %. "
      "Il n'y a aucun droit de douane entre les deux pays : la difficulté est économique, pas réglementaire.")

s = slide("4 · L'analyse", "Où ouvrir ? Cologne coche les 3 critères")
score = lambda v: (v["km_hub"] <= 450) + (v["magasins_par_100k"] <= 0.7) + (v["pop"] >= 1e6)  # noqa: E731
villes = sorted(D["villes"], key=lambda v: (-score(v), v["km_hub"]))
rows = [("Ville", "Habitants", "CECONOMY / 100 000 hab.", "Distance au hub", "Score")] + [
    (v["ville"], f"{n(v['pop'] / 1e6, 2)} M", n(v["magasins_par_100k"], 2), f"{n(v['km_hub'], 0)} km", f"{score(v)} / 3") for v in villes]
table(s, M, Inches(1.85), Inches(7.6), rows, [Inches(2.0), Inches(1.4), Inches(1.9), Inches(1.4), Inches(0.9)], size=13, h=Inches(3.6))
tb(s, M, Inches(5.6), Inches(7.6), Inches(1.3), [[("Critères : ", {"bold": True}), ("proche du hub (≤ 450 km), concurrence faible (≤ 0,7 magasin CECONOMY pour 100 000 hab.), grand bassin (≥ 1 million d'habitants). On se limite aux 7 plus grandes villes : ce sont celles qui peuvent faire vivre un magasin de 2 400 m².", {})]], size=13, color=MUTED)
xs, ws = M + Inches(7.9), prs.slide_width - M - (M + Inches(7.9))
stat(s, xs, Inches(1.85), ws, f"{n(KOLN['km_hub'], 0)} km", "de Cologne à l'entrepôt de Chilly-Mazarin : la plus proche des grandes villes", color=GREEN)
stat(s, xs, Inches(3.55), ws, f"{n(D['distance_moy'], 0)} → {n(D['distance_depuis_koln'], 0)} km", "distance moyenne aux 79 grandes villes, depuis la France puis depuis un entrepôt à Cologne", size=30)
lecture_ia(s, xs, Inches(5.25), ws, "villes", "Köln", h=Inches(1.45))
footer(s, "Destatis (population, coordonnées) ; magasins CECONOMY (plans des sites, rattachés aux communes) ; calcul de l'équipe")
notes(s, "6:00 → 6:45", "Elena", "Troisième question : où ouvrir. On ne regarde que les 7 plus grandes villes, celles qui peuvent faire "
      "vivre un grand magasin, et on les note sur trois critères simples. Cologne est la seule à cocher les trois : plus d'un million "
      f"d'habitants, peu de magasins du concurrent pour sa taille, et {n(KOLN['km_hub'], 0)} km de notre entrepôt. Un entrepôt en "
      f"Allemagne diviserait les distances par deux, mais pour un seul magasin, livrer depuis la France suffit. [DÉMO 30 s : dashboard, "
      "onglet « Où ouvrir ? », changer de ville ; le commentaire IA se réécrit en direct]")

s = slide("4 · L'analyse · + brique IA", "Un magasin n'est rentable qu'avec des achats en Allemagne et un loyer maîtrisé")
sc = list(D["scenarios"].values())
cd = CategoryChartData()
court = {"A": "A. achats France, loyer IHK", "B": "B. achats France, loyer France", "C": "C. achats locaux, loyer IHK", "D": "D. achats locaux, loyer France"}
cd.categories = [court[k] + " · " + sg(x["resultat"], 2) for k, x in D["scenarios"].items()]
cd.add_series("Perte", [round(x["resultat"], 2) if x["resultat"] < 0 else 0 for x in sc])
cd.add_series("Gain", [round(x["resultat"], 2) if x["resultat"] > 0 else 0 for x in sc])
ch = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, M, Inches(1.85), Inches(7.4), Inches(3.0), cd).chart
style(ch)
pl = ch.plots[0]
pl.gap_width, pl.overlap, pl.has_data_labels = 50, 100, False
for ser, col in zip(ch.series, (RED, GREEN)):
    ser.invert_if_negative = False
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = col
ch.category_axis.reverse_order = True
ch.category_axis.tick_label_position = XL_TICK_LABEL_POSITION.LOW
ch.category_axis.tick_labels.font.size = Pt(14)
ch.has_title = True
ch.chart_title.text_frame.text = "Résultat annuel d'un magasin de 2 400 m² (M€), 4 scénarios"
ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(15)
m = D["simu"]
ca = m["ca_magasin"] / 1e6
steps = [("Ventes", f"{n(ca, 1)} M€"), ("Marge 28 %", f"+{n(ca * 0.28, 2)}"), ("Salaires, frais", f"−{n(ca * m['couts_hors_loyer_pct'] / 100, 2)}"),
         ("Loyer", f"−{n(ca * m['loyers_pct'] / 100, 2)}"), ("Résultat", sg(SD["resultat"], 2))]
sw = Inches(7.4) / 5
for i, (lab, val) in enumerate(steps):
    x = M + i * sw
    box(s, x + Inches(0.05), Inches(5.0), sw - Inches(0.1), Inches(0.9), TINT)
    tb(s, x + Inches(0.15), Inches(5.05), sw - Inches(0.3), Inches(0.35), lab, size=11, color=MUTED)
    tb(s, x + Inches(0.15), Inches(5.38), sw - Inches(0.3), Inches(0.45), val, size=18, bold=True, color=GREEN if i == 4 else INK)
tb(s, M, Inches(6.0), Inches(7.4), Inches(0.9), "Calcul du scénario D en M€ par an : ventes au m² de la Fnac en France × 2 400 m² ; frais et loyer avec le poids qu'ils ont dans les comptes du groupe.", size=12, color=MUTED)
xs, ws = M + Inches(7.7), prs.slide_width - M - (M + Inches(7.7))
stat(s, xs, Inches(1.85), ws, f"{n(SD['delai'])} ans", "pour rembourser l'investissement (3,6 M€, hypothèse) dans le seul scénario rentable ; jamais dans les 3 autres", color=GREEN)
stat(s, xs, Inches(3.55), ws, f"< {n(D['seuil_loyer'], 0)} €", f"loyer maximal par m² et par mois ; la référence IHK (chambre de commerce allemande) est de {n(D['loyer_m2_mois'], 0)} €", color=BLUE)
lecture_ia(s, xs, Inches(5.25), ws, "kpi", "K12", h=Inches(1.45))
footer(s, "Document d'enregistrement universel 2025 p. 30, 32, 33, 40 ; IHK Stuttgart 2024 (loyer, hypothèse) ; investissement 1 500 €/m² (hypothèse non sourcée)")
notes(s, "6:45 → 7:30", "Romane", "Le cœur de l'analyse : on a calculé le résultat d'un magasin de 2 400 m² dans quatre scénarios, achats en "
      "France ou en Allemagne, loyer de centre-ville ou au niveau français. Trois sur quatre perdent de l'argent. Seul le scénario "
      f"achats allemands et loyer maîtrisé gagne {n(SD['resultat'], 2)} M€ par an, soit un retour en {n(SD['delai'])} ans. L'encadré "
      "violet est écrit par notre brique IA : elle ne calcule rien, elle commente nos KPI, et un script vérifie chaque chiffre qu'elle écrit.")

s = slide("4 · L'analyse", "La Fnac peut financer un pilote, pas un réseau")
cd = CategoryChartData()
lab = ["Investissements prévus / an", "Investissements 2025", "Cash-flow libre 2025", "Résultat net 2025", "Pilote (1 magasin)"]
val = [F["capex_moyen_plan"], F["investissements_operationnels"], F["cash_flow_libre_operationnel"], F["resultat_net_part_groupe"], 3.6]
cd.categories = [f"{a} · {sg(b, 1) if b < 0 else n(b, 1)} M€" for a, b in zip(lab, val)]
cd.add_series("Négatif", [v if v < 0 else 0 for v in val])
cd.add_series("Positif", [v if v > 0 else 0 for v in val])
ch = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, M, Inches(1.85), Inches(7.4), Inches(4.0), cd).chart
style(ch)
pl = ch.plots[0]
pl.gap_width, pl.overlap = 50, 100
for ser, col in zip(ch.series, (RED, BLUE)):
    ser.invert_if_negative = False
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = col
ch.category_axis.reverse_order = True
ch.category_axis.tick_label_position = XL_TICK_LABEL_POSITION.LOW
ch.has_title = True
ch.chart_title.text_frame.text = "Les moyens du groupe face au pilote (M€)"
ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(15)
xs, ws = M + Inches(7.7), prs.slide_width - M - (M + Inches(7.7))
stat(s, xs, Inches(1.85), ws, f"{n(F['cash_flow_libre_operationnel'], 0)} M€", f"de cash-flow libre en 2025 (210 M€ en 2024) : l'argent disponible après investissements", color=BLUE)
stat(s, xs, Inches(3.55), ws, f"{n(3.6 / F['cash_flow_libre_operationnel'] * 100, 1)} %", "du cash-flow libre : le coût du pilote, supportable", color=GREEN)
stat(s, xs, Inches(5.25), ws, f"{sg(F['resultat_net_part_groupe'], 1)} M€", "de résultat net en 2025 (dépréciations) : pas le moment d'ouvrir un réseau entier", color=RED)
footer(s, "Document d'enregistrement universel 2025 (chiffres publiés pour l'ensemble du groupe), p. 8, 21, 30, 31, 34 ; pilote : hypothèse")
notes(s, "7:30 → 8:00", "Elena", f"Dernière question : le groupe a-t-il les moyens ? le groupe Fnac a dégagé {n(F['cash_flow_libre_operationnel'], 0)} "
      f"millions d'euros de cash-flow libre en 2025 ; le pilote en coûte 3,6, soit {n(3.6 / F['cash_flow_libre_operationnel'] * 100, 1)} %. "
      f"Mais le résultat net est négatif, {n(F['resultat_net_part_groupe'], 1)} M€ : on peut financer un test, pas un déploiement national.")

# ============================================================ 5. GO / NO-GO (1 min 30)
s = slide("5 · Décision et recommandation · défense des arbitrages 15 pts", "", cover=True)
tb(s, M, Inches(1.35), CW, Inches(1.2), "GO SOUS CONDITIONS", size=60, bold=True, color=GREEN)
tb(s, M, Inches(2.6), CW, Inches(0.6), "Un seul magasin pilote, à Cologne.", size=28)
conds = [("Acheter en Allemagne", "pour garder 28 % de marge"), (f"Loyer < {n(D['seuil_loyer'], 0)} €/m²", "par mois, hors rue prime"), ("Tech + jeux vidéo", "90 % du catalogue vendable")]
cw = (CW - Inches(0.5)) / 3
for i, (t1, t2) in enumerate(conds):
    x = M + i * (cw + Inches(0.25))
    box(s, x, Inches(3.65), cw, Inches(1.5), CREAM)
    bar(s, x, Inches(3.73), Inches(0.08), Inches(1.34), GREEN)
    tb(s, x + Inches(0.3), Inches(3.85), cw - Inches(0.5), Inches(0.6), t1, size=24, bold=True)
    tb(s, x + Inches(0.3), Inches(4.5), cw - Inches(0.5), Inches(0.5), t2, size=16, color=MUTED)
tb(s, M, Inches(5.6), CW, Inches(0.5), "Décision de déploiement dans 3 ans, sur résultat réel.", size=20, bold=True)
notes(s, "8:00 → 9:30", "Romane", "Notre décision : Go sous conditions, pour un seul magasin pilote à Cologne, pas un réseau. Trois "
      "conditions : acheter en Allemagne pour retrouver notre marge ; un loyer sous 33 euros le mètre carré ; un assortiment centré "
      "sur la tech et les jeux vidéo. Cologne est la seule grande ville qui coche nos trois critères. Calendrier : centrale d'achat et "
      "bail dans les six premiers mois, ouverture à un an, décision de déploiement à trois ans, avec un critère d'arrêt écrit.")

s = slide("5 · Décision et recommandation", "Ce que nous demandons au Comex", cover=True)
asks = [("Valider le pilote de Cologne", "Un magasin de 2 400 m², pas un déploiement national."),
        ("Valider les 3 conditions", f"Achats en Allemagne · loyer < {n(D['seuil_loyer'], 0)} €/m²/mois · assortiment tech + jeux vidéo."),
        ("Fixer la décision à M36", "Résultat annuel positif et retour sur investissement en 8 ans au plus ; sinon, arrêt.")]
for i, (t1, t2) in enumerate(asks):
    y = Inches(2.3) + i * Inches(1.35)
    c = s.shapes.add_shape(MSO_SHAPE.OVAL, M, y, Inches(0.45), Inches(0.45))
    c.fill.solid(); c.fill.fore_color.rgb = YEL; c.line.fill.background(); c.shadow.inherit = False
    tb(s, M, y, Inches(0.45), Inches(0.45), str(i + 1), size=14, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    tb(s, M + Inches(0.75), y - Inches(0.02), Inches(10), Inches(0.5), t1, size=24, bold=True)
    tb(s, M + Inches(0.75), y + Inches(0.5), Inches(10), Inches(0.4), t2, size=15, color=MUTED)
tb(s, M, Inches(6.4), Inches(9), Inches(0.4), "Merci, nous sommes prêts pour vos questions.", size=15, color=MUTED)
notes(s, "9:30 → 10:00", "Romane", "Concrètement, nous demandons au Comex trois décisions : valider le pilote de Cologne, valider nos trois "
      "conditions, et fixer dès maintenant le rendez-vous de décision à trois ans avec un critère d'arrêt. Merci, nous sommes prêts "
      "pour vos questions.")

s = slide("Annexe · pour les questions", "Comment on a utilisé l'IA, et nos limites")
hw = (CW - Inches(0.4)) / 2
tb(s, M, Inches(1.9), hw, Inches(5.0), [
    [("La brique IA (Claude)", {"bold": True, "size": 18})],
    [("1. Chaque onglet du dashboard calcule ses chiffres selon les filtres.", {})],
    [("2. Il envoie à Claude uniquement ces chiffres + une consigne (visible dans la page).", {})],
    [("3. Claude rédige le commentaire en direct : rien n'est écrit à l'avance.", {})],
    [("4. La page vérifie chaque nombre de la réponse ; un nombre inconnu est surligné.", {})],
    [("Pourquoi : l'IA rédige bien mais calcule mal ; les calculs restent dans le code, traçables.", {"color": MUTED})]], size=14)
tb(s, M + hw + Inches(0.4), Inches(1.9), hw, Inches(5.0), [
    [("Nos limites", {"bold": True, "size": 18})],
    [("ROI = ordre de grandeur : ratios publiés pour l'ensemble du groupe (la Fnac seule n'est pas publiée), sans montée en charge ni impôts ; sensibilité 4,4 à 13,2 ans.", {})],
    [("Investissement 1 500 €/m² et loyer IHK : hypothèses.", {})],
    [("Catalogue éligible : simulé (catalogue Fnac non public).", {})],
    [("Livres : 350 €/hab. en Allemagne contre 155 € en France, écart inexpliqué, non utilisé.", {})],
    [("Magasins : 394 trouvés contre 403 publiés ; 4 villes homonymes non vérifiées.", {})]], size=14)
footer(s, "README du repo ; dashboard, onglet « IA & méthode » ; docs/questions_jury.md")
notes(s, "réserve", "Romane + Elena", "Slide de réserve. Si on nous demande comment on a utilisé l'IA : elle ne calcule rien ; elle "
      "reçoit nos chiffres et les commente en direct, et la page vérifie chaque nombre. Si le jury attaque le ROI : c'est un ordre "
      "de grandeur, et la sensibilité montre que la conclusion tient : il faut des achats locaux et un loyer maîtrisé dans tous les cas.")

# ---------- transitions en fondu sur toutes les slides + animation d'ouverture sur la couverture
P_NS = 'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'


def fondu(slide_):
    """Transition en fondu à l'entrée de la slide."""
    el = parse_xml(f'<p:transition {P_NS} spd="med"><p:fade/></p:transition>')
    slide_._element.insert(2, el)  # après cSld et clrMapOvr


def apparitions(slide_, shapes, pas_ms=700):
    """Les formes apparaissent l'une après l'autre en fondu, automatiquement à l'ouverture de la slide."""
    ids = iter(range(3, 100))
    effets = ""
    for k, shp in enumerate(shapes):
        a_, b_, c_, d_, e_ = (next(ids) for _ in range(5))
        effets += (f'<p:par><p:cTn id="{a_}" fill="hold"><p:stCondLst><p:cond delay="{k * pas_ms}"/></p:stCondLst><p:childTnLst>'
                   f'<p:par><p:cTn id="{b_}" presetID="10" presetClass="entr" presetSubtype="0" fill="hold" grpId="0" nodeType="{"withEffect" if k == 0 else "afterEffect"}">'
                   f'<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
                   f'<p:set><p:cBhvr><p:cTn id="{c_}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
                   f'<p:tgtEl><p:spTgt spid="{shp.shape_id}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
                   f'<p:to><p:strVal val="visible"/></p:to></p:set>'
                   f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{d_}" dur="900"/>'
                   f'<p:tgtEl><p:spTgt spid="{shp.shape_id}"/></p:tgtEl></p:cBhvr></p:animEffect>'
                   f'</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>')
    xml = (f'<p:timing {P_NS}><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
           f'<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
           f'<p:par><p:cTn id="99" fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst>'
           f'<p:childTnLst>{effets}</p:childTnLst></p:cTn></p:par>'
           f'</p:childTnLst></p:cTn><p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
           f'<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
           f'</p:childTnLst></p:cTn></p:par></p:tnLst>'
           f'<p:bldLst>{"".join(f'<p:bldP spid="{shp.shape_id}" grpId="0"/>' for shp in shapes)}</p:bldLst></p:timing>')
    slide_._element.append(parse_xml(xml))


for sl in prs.slides:
    fondu(sl)
couverture = prs.slides[0]
cibles = [sh for sh in couverture.shapes if sh.has_text_frame and (sh.text_frame.text == "Fnac → Allemagne" or sh.text_frame.text.startswith(("L'implantation", "Romane", "Projet final")))]
apparitions(couverture, cibles)

out = ROOT / "docs" / "Comex_Fnac_Allemagne.pptx"
prs.save(out)
md = ["# Script de l'oral (10 min)", "", "Généré par `src/restitution/build_slides.py` avec les chiffres du Gold. Le même texte est dans les notes "
      "de présentation du PowerPoint. Répartition Romane / Elena proposée, à ajuster.", ""]
for num, titre, minutage, qui, texte in SCRIPT:
    md += [f"## Slide {num} · {titre or 'Titre'}", f"**{minutage} · {qui}**", "", texte, ""]
(ROOT / "docs" / "script_oral.md").write_text("\n".join(md), encoding="utf-8")
print(f"{out.name} : {len(prs.slides)} slides ; script_oral.md : {len(SCRIPT)} sections")
