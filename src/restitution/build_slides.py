"""Gold -> docs/Comex_Fnac_Allemagne.pptx (9 slides, graphiques natifs) + docs/script_oral.md (ce qu'on dit, minuté).

Les slides suivent les 5 sections de l'oral imposées par le sujet (slide 8 du PDF « Data Analytics Project ») :
1. entreprise & pays (1 min) · 2. base de données & cadrage (1 min 30) · 3. pourquoi ces KPI (2 min)
· 4. analyse des chiffres + brique IA (3 min) · 5. Go / No-Go (1 min 30). Tous les chiffres sont lus dans le Gold.
"""
import json
import re

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION, XL_TICK_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import donnees  # noqa: E402
from paths import GOLD, ROOT

D = donnees.donnees()
AI = json.loads((GOLD / "commentaires_ia_filtres.json").read_text(encoding="utf-8"))
L = D["last"]
T = D["categories"]["TECH"]
NRW = next(x for x in D["lands"] if x["land"] == "Nordrhein-Westfalen")
SD = D["scenarios"]["D"]
# La décision n'apparaît qu'à la conclusion : on retire du commentaire IA de l'analyse les phrases qui l'annoncent
TEXTE_IA_D = " ".join(p for p in re.split(r"(?<=\.) ", AI["scenarios"]["D"]["texte"]) if "Go" not in p)

INK, DARK, WHITE = RGBColor(0x0B, 0x0B, 0x0B), RGBColor(0x14, 0x17, 0x22), RGBColor(0xFF, 0xFF, 0xFF)
BLUE, ORANGE, RED, GREEN = RGBColor(0x2A, 0x78, 0xD6), RGBColor(0xEB, 0x68, 0x34), RGBColor(0xD0, 0x3B, 0x3B), RGBColor(0x0C, 0xA3, 0x0C)
VIOLET, GREY, MUTED, LIGHT = RGBColor(0x62, 0x50, 0xD6), RGBColor(0xA3, 0xA2, 0x9C), RGBColor(0x52, 0x51, 0x4E), RGBColor(0xC3, 0xC2, 0xB7)
TINT, VTINT = RGBColor(0xF4, 0xF4, 0xF1), RGBColor(0xF1, 0xEF, 0xFC)
FONT = "Calibri"


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
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
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
    return box


def slide(section, title, dark=False):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = DARK if dark else WHITE
    tb(s, M, Inches(0.4), CW, Inches(0.35), section.upper(), size=12, bold=True, color=LIGHT if dark else MUTED)
    tb(s, M, Inches(0.75), CW, Inches(1.1), title, size=32, bold=True, color=WHITE if dark else INK)
    return s


def box(s, x, y, w, h, fill):
    shp = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    shp.adjustments[0] = 0.06
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def stat(s, x, y, w, value, label, color=INK, fill=TINT, label_color=MUTED, size=40):
    box(s, x, y, w, Inches(1.6), fill)
    tb(s, x + Inches(0.25), y + Inches(0.15), w - Inches(0.5), Inches(0.85), value, size=size, bold=True, color=color)
    tb(s, x + Inches(0.25), y + Inches(1.0), w - Inches(0.5), Inches(0.55), label, size=13, color=label_color)


def footer(s, txt, dark=False):
    tb(s, M, Inches(7.02), CW, Inches(0.3), txt, size=10, color=LIGHT if dark else MUTED)


def notes(s, minutage, qui, texte):
    """Notes de présentation (visibles en mode présentateur) + même texte dans docs/script_oral.md."""
    s.notes_slide.notes_text_frame.text = f"[{minutage} · {qui}]\n{texte}"
    titre = next(sh.text_frame.text for sh in list(s.shapes)[1:2])
    SCRIPT.append((len(prs.slides), titre, minutage, qui, texte))


def style(chart, legend=False):
    chart.font.name, chart.font.size = FONT, Pt(12)
    chart.has_legend = legend
    if legend:
        chart.legend.position, chart.legend.include_in_layout = XL_LEGEND_POSITION.TOP, False


# ============================================================ 1. ENTREPRISE & PAYS (1 min)
s = slide("Comex Fnac · Stratégie 2027-2029", "")
tb(s, M, Inches(1.7), CW, Inches(1.2), "Fnac → Allemagne", size=64, bold=True, color=INK)
box(s, M, Inches(3.05), Inches(0.12), Inches(1.5), BLUE)
tb(s, M + Inches(0.4), Inches(3.05), CW - Inches(0.4), Inches(1.5),
   "« L'implantation dans le pays ciblé est-elle réalisable et rentable ? »", size=28, color=MUTED, anchor=MSO_ANCHOR.MIDDLE)
tb(s, M, Inches(5.4), CW, Inches(0.5), "Romane LONG · Elena KERVENNIC · Arquam EL MEZOUARI EL GLAOUI · Samantha ASDRUBAL",
   size=16, color=INK)
footer(s, "Projet final Data Analytics · Eugenia School M2 · données publiques, aucune donnée interne réelle de la Fnac")
notes(s, "0:00 → 0:20", "Romane", "Bonjour. Le Comex de la Fnac nous pose une seule question : l'implantation en Allemagne "
      "est-elle réalisable et rentable ? Pour y répondre, on a construit toute la chaîne de données, du téléchargement jusqu'à "
      "la recommandation. Notre décision arrive à la fin ; voici d'abord le contexte.")

s = slide("1 · L'entreprise et le pays cible", "Une Fnac qui rétrécit en France, un marché allemand qui grandit")
stat(s, M, Inches(2.1), Inches(3.8), f"{D['x_magasins_fr']}", "magasins Fnac en France fin 2025\n(1 ouverture, 15 fermetures en 2025)", color=INK)
stat(s, M + Inches(4.05), Inches(2.1), Inches(3.8), sg(T["croissance_moy"]["DE"]) + " %/an",
     f"dépenses tech en Allemagne 2015-{L}\n(France : {sg(T['croissance_moy']['FR'])} %/an)", color=GREEN)
stat(s, M + Inches(8.1), Inches(2.1), Inches(4.0), "0", "magasin Fnac Darty en Allemagne\n(1er marché d'Europe : 83,6 M hab.)", color=BLUE)
tb(s, M, Inches(4.2), CW, Inches(2.4), [
    [("Périmètre : ", {"bold": True}), ("enseigne Fnac seule (biens culturels, produits techniques, services) ; Darty exclu.", {})],
    [("Pourquoi l'Allemagne : ", {"bold": True}), ("le plus grand marché d'Europe, absent du réseau Fnac Darty, et son leader MediaMarkt/Saturn est notre concurrent direct.", {})],
    [("Enjeu 2027-2029 : ", {"bold": True}), ("trouver la croissance hors de France sans détruire de valeur.", {})]], size=18)
footer(s, "Sources : Fnac Darty DEU 2025 p. 39 ; Eurostat nama_10_cp18 et demo_pjan ; fnacdarty.com « around the world »")
notes(s, "0:20 → 1:00", "Romane", f"La Fnac compte {D['x_magasins_fr']} magasins en France fin 2025, après 15 fermetures dans l'année. "
      f"En face, les dépenses des ménages allemands en produits techniques progressent de {n(T['croissance_moy']['DE'])} % par an "
      f"depuis 2015, quand elles reculent de {n(abs(T['croissance_moy']['FR']))} % en France. L'Allemagne est le premier marché "
      "d'Europe, le groupe n'y a aucun magasin, et son leader MediaMarkt-Saturn est déjà notre concurrent direct. "
      "C'est donc le pays le plus logique à tester.")

# ============================================================ 2. BASE DE DONNÉES & CADRAGE (1 min 30)
s = slide("2 · Base de données et cadrage · modélisation 20 pts + sources 15 pts", "Un pipeline reproductible, une source officielle par sujet")
img = ROOT / "docs" / "images" / "02_modele_etoile_flocon.png"
pic = s.shapes.add_picture(str(img), M, Inches(1.9), height=Inches(4.9))
x0 = M + pic.width + Inches(0.35)
w0 = prs.slide_width - x0 - M
tb(s, x0, Inches(1.95), w0, Inches(4.9), [
    [("Bronze → Silver → Gold", {"bold": True, "size": 20})],
    [("Téléchargé, nettoyé, puis modélisé par un script (run_pipeline.py) : relancé deux fois, résultat identique.", {})],
    [("Modèle en constellation", {"bold": True, "size": 20})],
    [("4 tables de faits, 6 dimensions, flocon commune → Land.", {})],
    [("Sources fiables", {"bold": True, "size": 20})],
    [("Eurostat, Destatis, rapports annuels déposés (Fnac Darty à l'AMF, CECONOMY), Commission européenne, EUR-Lex.", {})],
    [("Honnêteté", {"bold": True, "size": 20})],
    [("Chaque chiffre est étiqueté : mesuré, estimation, hypothèse ou simulé.", {})]], size=15)
footer(s, "Repo GitHub fnac-expansion-allemagne · README § 2 (dictionnaire, 11 règles de gestion) et § 3 (sources)")
notes(s, "1:00 → 2:30", "Elena", "Aucune donnée n'était fournie : on a tout collecté en données publiques. Le pipeline suit les trois "
      "couches vues en cours : Bronze, la donnée brute jamais modifiée ; Silver, une table propre par source ; Gold, le modèle "
      "en étoile. On a quatre tables de faits de grains différents qui partagent leurs dimensions, avec un flocon commune vers Land "
      "pour la zone de chalandise. Côté sources, une seule source officielle par sujet, pour ne jamais afficher deux chiffres "
      "différents : Eurostat pour le marché et les prix, Destatis pour les 10 753 communes, les rapports annuels pour les "
      "entreprises. Et tout ce qui n'est pas officiel est étiqueté hypothèse ou simulé.")

# ============================================================ 3. POURQUOI CES KPI (2 min)
s = slide("3 · La démarche analytique · choix des KPI 30 pts", "Un KPI par question du Comex, un KPI de synthèse pour trancher")
rows = [("Marché & potentiel", "Croissance du secteur · part de marché Fnac France · part du concurrent", "Quel plafond de CA ?"),
        ("Prix & marges", "Indice de prix DE/FR hors taxes · marge brute post-taxe", "Notre positionnement prix tient-il ?"),
        ("Réseau & implantation", "Densité concurrentielle par Land · coût au m²", "Où ouvrir, à quel coût ?"),
        ("Opérations & logistique", "Distance au hub de Chilly-Mazarin · douane et TVA", "Peut-on livrer depuis la France ?"),
        ("Assortiment", "Pénétration des catégories · % du catalogue éligible", "100 % du catalogue ou ciblé ?"),
        ("★ Synthèse", "Délai de retour sur investissement d'un magasin", "Go ou No-Go ?")]
tbl = s.shapes.add_table(len(rows) + 1, 3, M, Inches(1.95), CW, Inches(4.6)).table
tbl.columns[0].width, tbl.columns[1].width = Inches(3.0), Inches(5.6)
tbl.columns[2].width = CW - Inches(8.6)
for j, h in enumerate(["Axe du guide", "KPI retenus", "Décision éclairée"]):
    tbl.cell(0, j).text = h
for i, r in enumerate(rows, 1):
    for j, v in enumerate(r):
        tbl.cell(i, j).text = v
for i in range(len(rows) + 1):
    for j in range(3):
        c = tbl.cell(i, j)
        c.fill.solid()
        c.fill.fore_color.rgb = DARK if i == 0 else (VTINT if i == len(rows) else (TINT if i % 2 else WHITE))
        for p in c.text_frame.paragraphs:
            for r in p.runs:
                r.font.name, r.font.size = FONT, Pt(15)
                r.font.bold = i == 0 or j == 0
                r.font.color.rgb = WHITE if i == 0 else INK
footer(s, "12 KPI du guide du sujet + 1 KPI de synthèse · formules dans le README § 2.1 · calcul dans src/gold/kpi.py")
notes(s, "2:30 → 4:30", "Romane", "On a suivi le guide des KPI du Comex, axe par axe, et on s'est demandé pour chacun : quelle "
      "décision il éclaire. Le marché dit quel chiffre d'affaires est accessible. Les prix disent si notre positionnement tient. "
      "Le réseau dit où ouvrir et à quel coût. La logistique dit si on peut livrer depuis la France. L'assortiment dit si on vend "
      "tout le catalogue ou une sélection. Mais aucun de ces KPI ne répond seul à « rentable ? ». On a donc ajouté un KPI de "
      "synthèse : le délai de retour sur investissement d'un magasin, calculé à partir de tous les autres. Deux points de méthode : "
      "les parts de marché sont comparées hors taxes des deux côtés, et les prix sont comparés hors TVA.")

# ============================================================ 4. ANALYSE (3 min) : 3 slides
s = slide("4 · L'analyse · impact décisionnel & dataviz 35 pts", "Le marché allemand attire : deux fois plus gros et en croissance")
cd = CategoryChartData()
years = sorted(T["depenses"]["DE"])
cd.categories = [str(y) for y in years]
cd.add_series("Allemagne", [round(T["depenses"]["DE"][y] / 1000, 1) for y in years])
cd.add_series("France", [round(T["depenses"]["FR"][y] / 1000, 1) for y in years])
ch = s.shapes.add_chart(XL_CHART_TYPE.LINE, M, Inches(1.9), Inches(7.6), Inches(4.9), cd).chart
style(ch, legend=True)
for ser, col in zip(ch.series, (BLUE, ORANGE)):
    ser.format.line.color.rgb, ser.format.line.width, ser.smooth = col, Pt(3), False
ch.value_axis.has_major_gridlines = True
ch.value_axis.major_gridlines.format.line.color.rgb = RGBColor(0xE1, 0xE0, 0xD9)
ch.value_axis.tick_labels.font.size = Pt(11)
ch.has_title = True
ch.chart_title.text_frame.text = "Dépenses des ménages en produits techniques (Md€)"
ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(14)
xs = M + Inches(7.9)
ws = prs.slide_width - xs - M
stat(s, xs, Inches(1.9), ws, n(T["par_hab"]["DE"], 0) + " €", f"dépense tech par habitant en Allemagne\n(France : {n(T['par_hab']['FR'], 0)} €)", color=BLUE)
stat(s, xs, Inches(3.65), ws, "0 %", "droits de douane, TVA quasi identique\n(19 % contre 20 %)", color=GREEN)
stat(s, xs, Inches(5.4), ws, f"{n(D['parts']['cec_bas'], 0)}–{n(D['parts']['cec_haut'], 0)} %",
     "du marché tech déjà tenu par CECONOMY\n(MediaMarkt + Saturn, estimation)", color=RED)
footer(s, "Eurostat nama_10_cp18 (euros courants) ; CECONOMY Annual Report 2024/25 ; KPI K1, K3, K9, K10")
notes(s, "4:30 → 5:30", "Elena", f"Premier constat : le marché attire. Les ménages allemands dépensent {n(T['par_hab']['DE'], 0)} euros "
      f"par habitant en produits techniques, contre {n(T['par_hab']['FR'], 0)} en France, et la courbe monte quand la française "
      "stagne. Aucune barrière réglementaire : zéro droit de douane, une TVA quasi identique. Mais la place est prise : "
      f"CECONOMY, MediaMarkt et Saturn, tient entre {n(D['parts']['cec_bas'], 0)} et {n(D['parts']['cec_haut'], 0)} % du marché.")

s = slide("4 · L'analyse", "Mais les prix allemands écrasent notre marge")
cd = CategoryChartData()
yrs = sorted(T["marge"])
cd.categories = [str(y) for y in yrs]
cd.add_series("Marge brute en Allemagne à coût d'achat français (%)", [round(T["marge"][y], 1) for y in yrs])
ch = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, M, Inches(1.9), Inches(6.6), Inches(4.9), cd).chart
style(ch)
pl = ch.plots[0]
pl.gap_width, pl.has_data_labels = 60, True
pl.data_labels.number_format, pl.data_labels.number_format_is_linked = '0.0" %"', False
pl.data_labels.position, pl.data_labels.font.size = XL_LABEL_POSITION.OUTSIDE_END, Pt(14)
ch.series[0].format.fill.solid()
ch.series[0].format.fill.fore_color.rgb = RED
ch.value_axis.maximum_scale, ch.value_axis.minimum_scale = 30, 0
ch.value_axis.has_major_gridlines = False
ch.has_title = True
ch.chart_title.text_frame.text = "Marge brute estimée, produits techniques (groupe : 28 %)"
ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(14)
xs = M + Inches(6.9)
ws = prs.slide_width - xs - M
stat(s, xs, Inches(1.9), ws, n(T["indice_ht"][L], 0), f"indice de prix hors taxes {L}, France = 100\n→ produits tech 18 % moins chers", color=RED)
stat(s, xs, Inches(3.65), ws, f"{n(T['marge'][L])} %", "de marge si on achète en France\ncontre 28 % pour le groupe", color=RED)
box(s, xs, Inches(5.4), ws, Inches(1.6), VTINT)
tb(s, xs + Inches(0.25), Inches(5.55), ws - Inches(0.5), Inches(1.4), [[("Condition n° 1", {"bold": True, "color": VIOLET})],
   [("acheter en Allemagne (centrale d'achat locale) pour retrouver ~28 % de marge", {})]], size=16)
footer(s, "Eurostat prc_ppp_ind_1 (indices de niveau des prix, TTC → HT) ; Fnac Darty DEU 2025 p. 30 ; KPI K4, K5 (estimations)")
notes(s, "5:30 → 6:30", "Romane", f"Deuxième constat : les produits techniques sont environ 18 % moins chers en Allemagne, hors taxes. "
      f"Si la Fnac achète ses produits au prix français et les revend au prix allemand, sa marge brute tombe à {n(T['marge'][L])} %, "
      "contre 28 % pour le groupe. C'est la première condition : il faut acheter en Allemagne, via une centrale d'achat locale. "
      "Les livres résistent mieux, mais seuls 10 % de notre catalogue de livres, en français, est vendable là-bas.")

s = slide("4 · L'analyse · + brique IA", "Un seul scénario rentable : achats locaux et loyer maîtrisé")
cd = CategoryChartData()
sc = list(D["scenarios"].values())
cd.categories = [x["nom"] + " · " + sg(x["resultat"], 2) + " M€" for x in sc]
# Deux séries (perte / gain) superposées : couleur portée par la série, pas de barre négative inversée en blanc
cd.add_series("Perte", [round(x["resultat"], 2) if x["resultat"] < 0 else 0 for x in sc])
cd.add_series("Gain", [round(x["resultat"], 2) if x["resultat"] > 0 else 0 for x in sc])
ch = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, M, Inches(1.9), Inches(7.2), Inches(3.3), cd).chart
style(ch)
pl = ch.plots[0]
pl.gap_width, pl.overlap, pl.has_data_labels = 50, 100, False  # valeurs écrites dans les libellés
for ser, col in zip(ch.series, (RED, GREEN)):
    ser.invert_if_negative = False
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = col
ch.category_axis.reverse_order = True
ch.category_axis.tick_label_position = XL_TICK_LABEL_POSITION.LOW
ch.category_axis.tick_labels.font.size = Pt(12)
ch.value_axis.has_major_gridlines = False
ch.value_axis.tick_labels.font.size = Pt(10)
xs = M + Inches(7.5)
ws = prs.slide_width - xs - M
stat(s, xs, Inches(1.9), ws, f"{n(SD['delai'])} ans", "retour sur investissement, scénario D\n(3,6 M€ investis, hypothèse)", color=GREEN)
stat(s, xs, Inches(3.65), ws, f"< {n(D['seuil_loyer'], 0)} €", f"loyer maximal par m² et par mois\n(référence IHK : {n(D['loyer_m2_mois'], 0)} €)", color=BLUE)
box(s, M, Inches(5.4), prs.slide_width - 2 * M, Inches(1.5), VTINT)
tb(s, M + Inches(0.3), Inches(5.5), prs.slide_width - 2 * M - Inches(0.6), Inches(1.35), [
    [("✦ Synthèse IA (Claude, chiffres contrôlés contre nos KPI)", {"bold": True, "color": VIOLET, "size": 13})],
    [(TEXTE_IA_D, {"size": 15})]], size=15)
footer(s, "Hypothèses : surface 2 400 m² (DEU 2025 p. 40), coûts et loyers du groupe (DEU p. 30) ; investissement 1 500 €/m² non sourcé · KPI K12")
notes(s, "6:30 → 7:30", "Elena", "Troisième constat, le plus important. On a simulé le résultat d'un magasin de 2 400 mètres carrés "
      "dans quatre scénarios : achats en France ou en Allemagne, loyer de centre-ville ou loyer au niveau français. Trois sur quatre "
      f"perdent de l'argent. Seul le scénario achats locaux et loyer maîtrisé est rentable, avec un retour en {n(SD['delai'])} ans. "
      f"D'où la deuxième condition : un loyer sous {n(D['seuil_loyer'], 0)} euros le mètre carré par mois. Le commentaire en violet "
      "est rédigé par notre brique IA : elle lit uniquement nos KPI, et un script vérifie que chaque chiffre qu'elle écrit existe "
      "bien dans nos données. [DÉMO, 30 s] Dans le dashboard, onglet Rentabilité : changer le filtre Loyer, le commentaire IA "
      "change ; bouger le curseur Loyer du simulateur jusqu'à 33 euros, le verdict passe au rouge.")

# ============================================================ 5. GO / NO-GO (1 min 30)
s = slide("5 · Décision et recommandation · défense des arbitrages 15 pts", "GO SOUS CONDITIONS : un magasin pilote à Cologne")
conds = [("1", "Acheter en Allemagne", "centrale d'achat locale\nmarge brute ≈ 28 %"),
         ("2", f"Loyer < {n(D['seuil_loyer'], 0)} €/m²/mois", "grande surface hors rue prime\n(IHK : 115 €)"),
         ("3", "Assortiment ciblé", "tech + jeux vidéo (≈ 90 % éligibles)\npeu de livres en français")]
cw = (CW - Inches(0.5)) / 3
for i, (num, t1, t2) in enumerate(conds):
    x = M + i * (cw + Inches(0.25))
    box(s, x, Inches(1.95), cw, Inches(1.9), TINT)
    tb(s, x + Inches(0.25), Inches(2.05), cw - Inches(0.5), Inches(0.5), f"CONDITION {num}", size=12, bold=True, color=GREEN)
    tb(s, x + Inches(0.25), Inches(2.45), cw - Inches(0.5), Inches(0.6), t1, size=22, bold=True, color=INK)
    tb(s, x + Inches(0.25), Inches(3.05), cw - Inches(0.5), Inches(0.8), t2, size=14, color=MUTED)
tb(s, M, Inches(4.15), CW, Inches(0.4), "POURQUOI COLOGNE", size=12, bold=True, color=MUTED)
tb(s, M, Inches(4.5), CW, Inches(0.8), f"Rhénanie-du-Nord-Westphalie : {n(NRW['densite'])} magasins concurrents par million d'habitants "
   f"(moyenne {n(D['densite_de'])}) · Cologne à {n(NRW['ville_km'], 0)} km du hub de Chilly-Mazarin, la plus proche des villes de plus de 500 000 habitants.",
   size=16, color=INK)
steps = [("M1–M6", "centrale d'achat + bail"), ("M3–M6", "test logistique"), ("M12", "ouverture du pilote"), ("M36", "Go / No-Go déploiement")]
sw = CW / 4
for i, (when, what) in enumerate(steps):
    x = M + i * sw
    tb(s, x, Inches(5.55), sw - Inches(0.2), Inches(0.45), when, size=20, bold=True, color=BLUE)
    tb(s, x, Inches(6.0), sw - Inches(0.2), Inches(0.5), what, size=14, color=INK)
footer(s, "Critère d'arrêt à M36 : résultat annuel négatif ou retour > 8 ans → pas de déploiement. Détail : README § 4 Next Steps")
notes(s, "7:30 → 9:00", "Romane", "Notre décision : Go sous conditions, pour un seul magasin pilote, pas un réseau national. Trois "
      "conditions. Un : acheter en Allemagne pour retrouver notre marge. Deux : un loyer sous 33 euros le mètre carré, donc une "
      "grande surface hors des rues commerçantes les plus chères. Trois : un assortiment ciblé sur la tech et les jeux vidéo. "
      f"Pourquoi Cologne : sa région a l'une des densités concurrentes les plus faibles, {n(NRW['densite'])} magasins par million "
      f"d'habitants, et c'est la grande ville la plus proche de notre entrepôt, à {n(NRW['ville_km'], 0)} kilomètres. Calendrier : "
      "centrale d'achat et bail dans les six premiers mois, ouverture à un an, et décision de déploiement après deux ans "
      "d'exploitation, avec un critère d'arrêt écrit : si le magasin perd de l'argent ou si le retour dépasse 8 ans, on s'arrête.")

s = slide("Pour les questions", "Nos limites, dites avant qu'on nous les pose")
tb(s, M, Inches(1.95), CW, Inches(5), [
    [("ROI = ordre de grandeur. ", {"bold": True}), ("Ratios du groupe Fnac Darty (la Fnac seule n'est pas publiée) ; ni montée en charge, ni impôts, ni BFR. Sensibilité : 4,4 à 13,2 ans.", {})],
    [("Investissement 1 500 €/m² : ", {"bold": True}), ("hypothèse non sourcée.", {})],
    [("Loyer IHK : ", {"bold": True}), ("petites boutiques de Stuttgart ; aucun loyer vérifié à Cologne.", {})],
    [("Catalogue éligible : ", {"bold": True}), ("simulé (le catalogue Fnac n'est pas public).", {})],
    [("Livres : ", {"bold": True}), ("Eurostat donne 350 €/hab. en Allemagne contre 155 € en France ; écart inexpliqué, non utilisé comme argument.", {})],
    [("Magasins concurrents : ", {"bold": True}), ("394 trouvés contre 403 publiés (2 % d'écart).", {})]], size=18)
footer(s, "Tout est documenté dans le README et dans data/gold/kpi.csv (colonne « nature »)")
notes(s, "9:00 → 10:00", "Romane + Elena", "Slide de réserve pour les questions. Si le jury attaque le ROI : c'est un ordre de grandeur, "
      "on l'assume, et la sensibilité montre que la conclusion tient : il faut des achats locaux et un loyer maîtrisé dans tous les cas. "
      "Si on nous demande pourquoi pas les livres : seuls 10 % du catalogue de livres est vendable, puisqu'il est en français.")

out = ROOT / "docs" / "Comex_Fnac_Allemagne.pptx"
prs.save(out)
md = ["# Script de l'oral (10 min)", "", "Généré par `src/restitution/build_slides.py` avec les chiffres du Gold. Le même texte est dans les notes "
      "de présentation du PowerPoint. Répartition Romane / Elena proposée, à ajuster.", ""]
for num, titre, minutage, qui, texte in SCRIPT:
    md += [f"## Slide {num} · {titre or 'Titre'}", f"**{minutage} · {qui}**", "", texte, ""]
(ROOT / "docs" / "script_oral.md").write_text("\n".join(md), encoding="utf-8")
print(f"{out.name} : {len(prs.slides)} slides ; script_oral.md : {len(SCRIPT)} sections")
