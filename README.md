# Fnac en Allemagne : implantation réalisable et rentable ?

Projet final du cours Data Analytics (Eugenia School, M2). Le Comex de la Fnac étudie, dans sa stratégie 2027-2029, une implantation dans un pays européen hors France. Ce repo collecte, structure et analyse les données nécessaires pour répondre à une seule question :

> **L'implantation de la Fnac en Allemagne est-elle réalisable et rentable ?**

---

## 1. Présentation de l'entreprise

**La Fnac** est une enseigne du groupe **Fnac Darty**, coté à la Bourse de Paris. Le groupe se présente comme un « leader européen de la distribution de biens culturels, de loisirs, de produits techniques, d'électroménager et de services ». En 2024, il a réalisé près de 8 milliards d'euros de chiffre d'affaires, avec environ 25 000 collaborateurs. Les ventes en ligne représentent 22 % de ce chiffre d'affaires. *(DEU 2024, p. 18)*

**Périmètre retenu : l'enseigne Fnac seule.** Darty (électroménager) et Nature & Découvertes sont exclus de l'étude.

| Élément | Valeur | Source |
|---|---|---|
| Activité en France | Distribution omnicanale (magasins et fnac.com) de biens culturels et de produits techniques | DEU 2024, p. 18 |
| **Nombre de magasins Fnac en France (X)** | **205** à fin 2025 | DEU 2025, p. 39 *(voir l'encadré ci-dessous)* |
| Évolution du réseau français en 2025 | 1 ouverture, 15 fermetures | DEU 2025, p. 39 |
| Catalogue produits | Biens culturels et de loisirs (dont jeux et jouets depuis 2011), produits techniques, services | DEU 2024, p. 18 et 27 |
| Pays où la Fnac est déjà présente en Europe | France, Belgique, Luxembourg, Suisse, Espagne, Portugal | Site Fnac Darty, « Fnac Darty around the world » |
| **Pays ciblé** | **Allemagne** | voir ci-dessous |

> **Pourquoi 205 et pas 219 ?** Le DEU 2025 indique « 317 magasins au total, parmi lesquels 219 magasins situés en France ». Sa note de bas de page précise que ces 219 incluent 14 magasins à l'étranger (Tunisie, Qatar, Sénégal, Côte d'Ivoire, Congo, Cameroun, Arabie saoudite). Les magasins réellement situés en France sont donc 219 − 14 = **205**.

**Pourquoi l'Allemagne ?**
- C'est le premier marché d'Europe par sa population : 83,6 millions d'habitants contre 68,9 millions en France au 1er janvier 2025 (Eurostat, `demo_pjan`).
- Le groupe Fnac Darty n'y est pas présent.
- Son leader, MediaMarkt/Saturn, est le concurrent direct de la Fnac sur les produits techniques.

### Équipe

| Prénom | Nom |
|---|---|
| Romane | LONG |
| Elena | KERVENNIC |
| Arquam | EL MEZOUARI EL GLAOUI |
| Samantha | ASDRUBAL |

---

## 2. Cadrage & dictionnaire de données

*À venir : métriques, dimensions, règles de gestion, définitions des termes métier.*

## 3. Architecture & choix des sources

*À venir : une source fiable par sujet, avec la justification de chacune.*

```
data/manual/   Chiffres relevés à la main dans des documents officiels (source + page)
data/raw/      Bronze : données téléchargées par les scripts, jamais modifiées
data/silver/   Silver : données nettoyées, un fichier par source
data/gold/     Gold   : modèle en étoile + KPI
src/collect/   Un script de téléchargement par source
src/clean/     Un script de nettoyage par source
docs/          Livrables : dashboard, slides, images
```

Les données Bronze et Silver sont versionnées : le dépôt garde une copie figée de ce qui a été téléchargé, même si la source est mise à jour ensuite. Eurostat a, par exemple, publié une révision le 10/11/2026. Pour tout régénérer : `python run_pipeline.py`.

**Licences des données réutilisées**
- Eurostat : © Union européenne, 1995-2026, licence [CC BY 4.0](https://ec.europa.eu/eurostat/help/copyright-notice). Données transformées par l'équipe : dépliage du format JSON-stat et sélection DE / FR.
- Statistisches Bundesamt (Destatis), *Gemeindeverzeichnis 31.12.2025*, licence [dl-de/by-2-0](https://www.govdata.de/dl-de/by-2-0). Données transformées par l'équipe : sélection des communes, conversion des coordonnées, retrait des zones sans habitants.

## 4. Plan d'organisation & roadmap

*À venir.*

## 5. Stack technique

*À venir.*

---

## Sources citées

- **DEU 2024** : Fnac Darty, *Document d'enregistrement universel 2024*. https://fnacdarty.com/wp-content/uploads/2025/03/fnac-darty-deu-2024-assemblage-mel-opti.pdf
- **DEU 2025** : Fnac Darty, *Document d'enregistrement universel 2025*, déposé à l'AMF le 06/03/2026. https://www.fnacdarty.com/wp-content/uploads/2026/03/fnac-darty-deu-2025-assemblage-pdf-opti-1.pdf
- **Fnac Darty around the world** : https://www.fnacdarty.com/en/group/fnac-darty-around-the-world/
- **Eurostat `demo_pjan`** : population au 1er janvier. https://ec.europa.eu/eurostat/databrowser/view/demo_pjan/default/table
