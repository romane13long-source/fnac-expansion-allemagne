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

**Question du Comex :** l'implantation de la Fnac en Allemagne est-elle réalisable et rentable ?
**Périmètre :** enseigne Fnac (biens culturels et produits techniques), Allemagne comparée à la France, de 2015 à 2025 selon les sources.

### 2.1 Métriques (KPI)

Un KPI par question du guide fourni par le Comex, et un KPI de synthèse qui répond à « rentable ? ».

| Axe | KPI | Formule | Données utilisées | Ce qu'il permet de décider |
|---|---|---|---|---|
| Marché & potentiel | **Taux de croissance annuel du secteur** | (dépenses des ménages N / dépenses N-1) − 1, par catégorie et par pays | `fact_marche` | Le marché allemand grandit-il ? |
| Marché & potentiel | **Part de marché de Fnac Darty en France** *(estimation)* | CA France **HT** × (part produits techniques + part produits éditoriaux) / dépenses FR **ramenées HT** (TVA 20 % TECH, 5,5 % LIVRES) | `fact_indicateurs_officiels`, `fact_marche` | Quelle part la Fnac sait-elle prendre sur son marché d'origine ? |
| Marché & potentiel | **Part de marché du concurrent en Allemagne** *(fourchette)* | basse : ventes CECONOMY DE **HT** × part « IT et mobile » / dépenses DE TECH **ramenées HT** (TVA 19 %) ; haute : ventes CECONOMY DE **HT** / dépenses DE TECH **ramenées HT** | `fact_indicateurs_officiels`, `fact_marche` | Le marché est-il déjà verrouillé ? |
| Prix & marges | **Indice de prix relatif DE / FR** | indice de niveau des prix DE / indice FR × 100 (TTC), puis hors taxes : (indice DE / (1 + TVA DE de la catégorie)) / (indice FR / (1 + TVA FR de la catégorie)) × 100 | `fact_marche`, `fact_indicateurs_officiels` | Les prix allemands permettent-ils le positionnement de la Fnac ? |
| Prix & marges | **Marge brute estimée post-taxe** | 1 − (1 − taux de marge brute du groupe) / (indice relatif hors taxes / 100), à coût d'achat identique et avec la TVA de la catégorie | idem | La marge reste-t-elle suffisante au prix allemand ? |
| Réseau & implantation | **Densité concurrentielle par zone de chalandise** | magasins CECONOMY du Land / population du Land × 1 000 000 | `fact_magasins_concurrents`, `dim_commune`, `dim_land` | Dans quels Länder ouvrir en premier ? |
| Réseau & implantation | **Pression concurrentielle nationale** *(complément, borne haute)* | (magasins CECONOMY + points de vente Expert + Euronics) / population DE × 1 000 000 | `fact_magasins_concurrents`, `concurrents_autres` (Silver), `fact_population` | La densité CECONOMY sous-estime-t-elle la concurrence ? |
| Réseau & implantation | **Coût moyen au m² commercial** *(hypothèse)* | loyer de référence mensuel × 12 (€/m²/an) ; loyer d'un magasin = × 2 400 m² | hypothèse documentée (§ 3) | Quel coût pour chaque ouverture ? |
| Opérations & logistique | **Distance moyenne depuis le hub** | distance à vol d'oiseau (formule de haversine) entre le hub et chaque ville de 100 000 habitants ou plus, moyenne pondérée par la population | `dim_commune`, hub | Livrer depuis la France, ou ouvrir un entrepôt en Allemagne ? |
| Opérations & logistique | **Droits de douane / taxes locales** | droits de douane entre pays de l'UE ; écart de TVA DE − FR | `fact_indicateurs_officiels` | Surcoût réglementaire du passage de frontière |
| Assortiment | **Taux de pénétration des catégories** | (dépenses DE / population DE) / (dépenses FR / population FR) × 100, par catégorie | `fact_marche`, `fact_population` | Quelles catégories vendre en priorité ? |
| Assortiment | **% du catalogue France éligible** *(simulé)* | part des références du catalogue vendables en Allemagne | données simulées, signalées comme telles | 100 % du catalogue ou un assortiment ciblé ? |
| Synthèse | **Délai de retour sur investissement d'un magasin** | investissement d'ouverture / résultat annuel estimé d'un magasin | KPI ci-dessus | Go / No-Go |

> **Parts de marché : comparaison HT / HT.** Le CA des entreprises est publié hors taxes ; les dépenses des ménages Eurostat sont TTC. Les formules ci-dessus ramènent donc le marché à un montant HT avant de calculer une part (TVA 20 % FR / 19 % DE pour TECH ; 5,5 % FR / 7 % DE pour LIVRES). Sans cette correction, la part est sous-estimée d'environ 17 % pour TECH et 5 % pour LIVRES (`1 − 1/1,20` et `1 − 1/1,055`).
>
> **Densité concurrentielle.** Le KPI géolocalisé ne compte que CECONOMY (MediaMarkt + Saturn), seul réseau dont chaque magasin est connu. Les autres enseignes (Expert, Euronics, Amazon, Otto) sont suivies au niveau national dans `concurrents_autres` : elles documentent la pression concurrentielle, mais ne peuvent pas être affectées à un Land sans leur propre géolocalisation.

### 2.2 Dimensions (axes d'analyse)

| Dimension | Clé | Valeurs | Usage |
|---|---|---|---|
| `dim_pays` | `pays_id` | DE, FR, GROUPE | Comparer l'Allemagne à la France ; GROUPE pour les chiffres publiés au niveau d'un groupe entier |
| `dim_annee` | `annee` | 2015 → 2026 | Suivre une évolution, calculer une croissance |
| `dim_categorie` | `categorie_id` | TECH, LIVRES | Séparer les deux métiers de la Fnac |
| `dim_commune` | `code_commune` | 10 753 communes allemandes | Localiser les concurrents, mesurer les distances |
| `dim_land` | `land_code` | 16 Länder | Zone de chalandise à l'échelle régionale (flocon de `dim_commune`) |
| `dim_indicateur` | `indicateur_id` | 21 indicateurs relevés dans les rapports | Tracer la source et la page de chaque chiffre |

### 2.3 Règles de gestion

1. **Une source par sujet.** Si deux sources donnent un chiffre pour la même chose, on n'en garde qu'une, pour ne jamais afficher deux valeurs différentes.
2. **Une année commune.** Une date (« 2025-12-31 ») donne son année. Un exercice décalé (« 2024/25 ») est rattaché à son **année de clôture** (2025). Un taux en vigueur est daté de l'année de consultation.
3. **Valeurs provisoires gardées.** Eurostat marque certaines valeurs « provisoire ». On les garde, avec la mention dans `statut_eurostat`, et on le signale dans les visuels.
4. **Zones sans habitants exclues.** 200 « communes » sans habitants (forêts, lacs, eaux côtières) sont retirées : on ne peut pas y ouvrir de magasin.
5. **Un seul concurrent par groupe.** MediaMarkt et Saturn appartiennent à CECONOMY : ils forment **un** concurrent. Un magasin listé sur les deux sites (même identifiant) est compté une fois. Les autres enseignes (Expert, Euronics, Amazon, Otto) sont suivies séparément dans `concurrents_autres`.
6. **Rattachement magasin → commune**, du plus sûr au moins sûr : table manuelle, puis nom exact, puis début du nom officiel. Un mot générique seul (« Bad », « Sankt ») ne suffit jamais. La méthode utilisée est gardée dans `methode_rattachement`.
7. **Chiffre de groupe.** Un chiffre publié pour un groupe entier (CECONOMY, Fnac Darty) porte le pays `GROUPE`. Une clé n'est jamais vide.
8. **Correspondance des catégories.** TECH a la même définition dans le marché et dans les prix (`exacte`). LIVRES n'a pas d'indice de prix propre : on utilise celui des loisirs et de la culture (`approximative`).
9. **Prix et parts comparés à TVA homogène.** Les indices de prix Eurostat et les dépenses des ménages sont TTC ; le CA des entreprises est HT. On ne compare jamais un CA HT à un marché TTC : pour les parts de marché, les dépenses sont ramenées HT en les divisant par (1 + TVA du pays et de la catégorie) ; pour la marge, la TVA est retirée du prix. Taux retenus : TECH 20 % FR / 19 % DE ; LIVRES 5,5 % FR / 7 % DE (taux réduit appliqué à tout le poste, approximation).
10. **Hypothèses et données simulées signalées.** Toute valeur qui ne vient pas d'une source officielle est marquée « hypothèse » ou « simulé ».
11. **Périmètre concurrentiel à deux niveaux.** La densité géolocalisée porte sur CECONOMY, seul réseau connu magasin par magasin. Les autres enseignes sont suivies au niveau national dans `concurrents_autres` et servent de borne de pression concurrentielle, sans être imputées à un Land.

### 2.4 Termes métier

| Terme | Définition |
|---|---|
| **Zone de chalandise** (« zone d'achalandage ») | Territoire d'où vient la clientèle d'un magasin. Ici, approché par le Land. |
| **Indice de niveau des prix** (PLI) | Prix d'un panier de produits dans un pays, comparé à la moyenne de l'UE (= 100). Au-dessus de 100, le pays est plus cher. |
| **COICOP** | Nomenclature internationale qui classe les dépenses des ménages par fonction (ex. 08.1 = équipements d'information et de communication). Version 2018 utilisée. |
| **Dépenses de consommation des ménages** | Ce que les ménages d'un pays dépensent dans une catégorie : la taille du marché. |
| **Part de marché** | Ventes d'une entreprise / taille totale du marché. |
| **Taux de marge brute** | (Chiffre d'affaires − coût d'achat des produits vendus) / chiffre d'affaires. |
| **TVA** | Taxe sur la valeur ajoutée, incluse dans le prix payé par le client et reversée à l'État. Taux normal : 19 % en Allemagne, 20 % en France ; taux réduit : 7 % en Allemagne, 5,5 % en France (livres). |
| **HT / TTC** | Hors taxes / toutes taxes comprises. Le CA est publié HT, les dépenses des ménages et les prix payés sont TTC : on convertit avant toute comparaison. |
| **Union douanière** | Les marchandises circulent entre pays de l'UE sans droits de douane. |
| **Taux de pénétration** | Dépense par habitant dans une catégorie, comparée à un pays de référence. |
| **Prix unique du livre** | En Allemagne (Buchpreisbindungsgesetz) comme en France (loi Lang), l'éditeur fixe le prix de vente du livre : un libraire ne peut pas le casser. |
| **Exercice décalé** | Année comptable qui ne suit pas l'année civile. CECONOMY clôture au 30 septembre. |
| **Hub logistique** | Entrepôt d'où partent les produits vers les magasins et les clients. |

### 2.5 Dictionnaire des données

Format du cours : Champ / Type de donnée / Description / Formule / Exemple / Source. Les exemples sont de vraies valeurs des tables Silver.

**`marche`**, dépenses des ménages par pays, année et catégorie (44 lignes)

| Champ | Type de donnée | Description | Formule | Exemple | Source |
|---|---|---|---|---|---|
| `pays` | Texte (clé) | Code pays ISO à 2 lettres | NA | FR | Eurostat `nama_10_cp18` |
| `annee` | Entier (clé) | Année civile | NA | 2025 | idem |
| `categorie_code` | Texte (clé) | Code COICOP 2018 de la catégorie | NA | CP097 | idem |
| `categorie` | Texte | Libellé Eurostat de la catégorie | NA | Newspapers, books and stationery | idem |
| `depenses_menages_meur` | Numérique | Dépenses de consommation des ménages, en millions d'euros courants | NA | 10 674,7 | idem |
| `statut_eurostat` | Texte | Avertissement Eurostat (vide si valeur définitive) | NA | provisoire | idem |

**`prix`**, indices de niveau des prix (16 lignes)

| Champ | Type de donnée | Description | Formule | Exemple | Source |
|---|---|---|---|---|---|
| `pays`, `annee` | Texte, entier (clé) | Pays et année | NA | FR, 2025 | Eurostat `prc_ppp_ind_1` |
| `categorie_code` | Texte (clé) | Catégorie de l'indice (A010801 = même périmètre que CP081) | NA | A0109 | idem |
| `categorie` | Texte | Libellé Eurostat | NA | Recreation, sport and culture | idem |
| `indice_niveau_prix_ue100` | Numérique | Niveau des prix TTC, moyenne UE = 100 | prix du pays / prix moyen UE × 100 | 102,5 | idem |
| `statut_eurostat` | Texte | Avertissement Eurostat | NA | (vide) | idem |

**`population`**, population au 1er janvier (22 lignes)

| Champ | Type de donnée | Description | Formule | Exemple | Source |
|---|---|---|---|---|---|
| `pays`, `annee` | Texte, entier (clé) | Pays et année | NA | FR, 2025 | Eurostat `demo_pjan` |
| `population_1er_janvier` | Entier | Nombre d'habitants au 1er janvier | NA | 68 882 600 | idem |
| `statut_eurostat` | Texte | Avertissement Eurostat | NA | provisoire | idem |

**`communes`**, communes allemandes habitées (10 753 lignes)

| Champ | Type de donnée | Description | Formule | Exemple | Source |
|---|---|---|---|---|---|
| `code_commune` | Texte (clé) | Code officiel de la commune (AGS, 8 chiffres) | Land + district + arrondissement + commune | 01001000 | Destatis, Gemeindeverzeichnis 31.12.2025 |
| `nom` | Texte | Nom officiel | NA | Flensburg, Stadt | idem |
| `land_code` | Texte (clé étrangère) | Code du Land | NA | 01 | idem |
| `land_nom` | Texte | Nom du Land | NA | Schleswig-Holstein | idem |
| `population` | Entier | Habitants au 31/12/2025 (base recensement 2022) | NA | 95 568 | idem |
| `superficie_km2` | Numérique | Superficie | NA | 56,73 | idem |
| `longitude`, `latitude` | Numérique | Coordonnées du centre de la commune (degrés) | virgule décimale convertie en point | 9,43751 / 54,78252 | idem |

**`magasins_concurrents`**, magasins MediaMarkt et Saturn en Allemagne (394 lignes)

| Champ | Type de donnée | Description | Formule | Exemple | Source |
|---|---|---|---|---|---|
| `magasin_id` | Entier (clé) | Identifiant du magasin, commun aux deux sites | nombre en fin d'adresse de la page | 201 | Plans de site mediamarkt.de / saturn.de |
| `enseigne` | Texte | Site où le magasin a été trouvé en premier | NA | mediamarkt | idem |
| `page` | Texte | Nom de la page du magasin | NA | Erlangen-201 | idem |
| `nom_page` | Texte | Nom de ville extrait et normalisé | minuscules, ü → ue, préfixes retirés | erlangen | calculé |
| `methode_rattachement` | Texte | Comment le magasin a été relié à sa commune | règle de gestion n° 6 | nom exact | calculé |
| `liste_sur_les_deux_sites` | Booléen | Le magasin apparaît chez MediaMarkt et chez Saturn | NA | False | calculé |
| `code_commune` | Texte (clé étrangère) | Commune du magasin | jointure sur le nom normalisé | 09562000 | Destatis |
| `commune`, `land_code`, `land_nom`, `longitude`, `latitude` | Texte, numérique | Attributs de la commune rattachée | NA | Erlangen, 09, Bayern | Destatis |

**`sources_officielles`**, chiffres relevés dans des documents officiels (22 lignes)

| Champ | Type de donnée | Description | Formule | Exemple | Source |
|---|---|---|---|---|---|
| `indicateur` | Texte (clé) | Nom de l'indicateur | NA | fnac_magasins_total | relevé par l'équipe |
| `pays` | Texte (clé) | Pays concerné ; vide = chiffre de groupe (GROUPE dans le Gold) | NA | (vide) | idem |
| `valeur` | Numérique | Valeur publiée | NA | 317 | document cité |
| `unite` | Texte | Unité de la valeur | NA | magasins | idem |
| `periode` | Texte | Période telle qu'écrite dans le document | NA | 2025-12-31 | idem |
| `annee` | Entier | Année de rattachement | règle de gestion n° 2 | 2025 | calculé |
| `source`, `page`, `url` | Texte | Document, page et lien officiel | NA | Fnac Darty - DEU 2025, p. 39 | idem |

**`concurrents_autres`**, autres enseignes concurrentes en Allemagne (4 lignes)

| Champ | Type de donnée | Description | Formule | Exemple | Source |
|---|---|---|---|---|---|
| `enseigne` | Texte (clé) | Nom de l'enseigne | NA | Expert | relevé par l'équipe |
| `groupe` | Texte | Groupe ou centrale d'achat | NA | Expert SE | idem |
| `canal` | Texte | `magasin` ou `en ligne` | NA | magasin | idem |
| `pays` | Texte (clé) | Pays | NA | DE | idem |
| `nb_points_de_vente` | Entier | Nombre de points de vente en Allemagne (borne basse « plus de … ») ; 0 = pure player | NA | 400 | source citée |
| `periode` | Texte | Période telle qu'écrite dans la source | NA | consulté 2026-11-12 | idem |
| `annee` | Entier | Année de rattachement | règle de gestion n° 2 | 2026 | calculé |
| `source`, `url` | Texte | Document et lien officiel | NA | expert.de - Daten und Fakten | idem |
| `commentaire` | Texte | Positionnement et limite | NA | Réseau coopératif de proximité | idem |

**`kpi.csv`** (Gold), une ligne par valeur de KPI : `kpi_id` (K1a … K12), `axe` (axe du guide des KPI), `kpi`, `pays_id`, `categorie_id`, `zone` (Land, scénario ou famille), `annee`, `valeur`, `unite`, `nature` (mesuré / estimation / hypothèse / simulé), `formule`. Exemple : K12, « D. achats locaux + loyer niveau France », 7,94 années, estimation. Lu par le dashboard et par la brique IA.

**`catalogue_simule.csv`** (Gold, **simulé**) : `reference_id`, `famille`, `categorie_id`, `specifique_france`, `eligible_allemagne`, `nature`. 10 000 références fictives (graine fixe), règles dans `src/gold/catalogue_simule.py`.

**`hubs_logistiques`** (1 ligne) : `hub`, `commune`, `code_insee` (clé), `longitude`, `latitude`, `statut`, `source`, `url`. Exemple : Plateforme Fnac Darty Chilly-Mazarin, 91161, 2,3103 / 48,7051. Source : communiqué Fnac Darty et API Découpage administratif (geo.api.gouv.fr).

**`correspondance_categories`** (2 lignes) : `categorie_id` (clé), `categorie_fr`, `code_marche_eurostat`, `code_prix_eurostat`, `correspondance` (exacte / approximative), `commentaire`. Exemple : TECH, CP081, A010801, exacte. Table créée par l'équipe (règle de gestion n° 8).

### 2.6 Modèle de données

**Modèle relationnel** (tables Silver du modèle en étoile et leurs clés) :

![Modèle relationnel](docs/images/01_modele_relationnel.png)

**Modèle cible** (Gold) : quatre tables de faits de grains différents, qui partagent leurs dimensions (constellation), avec un flocon `dim_commune → dim_land` :

![Modèle en étoile / flocon](docs/images/02_modele_etoile_flocon.png)

> `concurrents_autres` est une table de référence **nationale** : elle n'a pas de grain magasin et n'entre donc pas dans le modèle en étoile. Elle sert à documenter la pression concurrentielle hors CECONOMY.

## 3. Architecture & choix des sources

### 3.1 Architecture

Le pipeline suit les couches vues en cours : on ne modifie jamais la donnée brute, chaque étape produit une nouvelle table.

```
 SOURCES                 BRONZE (data/raw)          SILVER (data/silver)        GOLD (data/gold)
 API Eurostat     ──►  JSON bruts         ──►  marche, prix, population  ──┐
 Destatis (xlsx)  ──►  fichier communes   ──►  communes                    ├──►  4 tables de faits
 Plans de site    ──►  sitemaps XML       ──►  magasins_concurrents        │    + 6 dimensions
 Rapports (PDF)   ──►  data/manual (CSV)  ──►  sources_officielles        ──┘    → KPI → dashboard + IA
 Pages officielles ──►  data/manual (CSV)  ──►  concurrents_autres (réf. nationale)
             src/collect/*.py          src/clean/*.py (contrôles)
```

Chaque script de nettoyage **s'arrête** si une règle est violée : doublon de clé, valeur négative, coordonnée hors d'Allemagne, chiffre sans source.

### 3.2 Une source par sujet

Règle : un seul jeu de données par sujet, pour ne jamais avoir deux chiffres différents pour la même chose.

| Sujet | Source retenue | Type | Pourquoi elle est fiable et pertinente | Limite connue |
|---|---|---|---|---|
| Marché | Eurostat `nama_10_cp18` (dépenses des ménages, COICOP 2018) | API open data | Office statistique de l'UE : même définition pour DE et FR, séries jusqu'en 2025 | Valeurs récentes « provisoires » |
| Prix | Eurostat `prc_ppp_ind_1` (indices de niveau des prix) | API open data | Même nomenclature que le marché : les chiffres se comparent directement | Pas d'indice pour les livres seuls |
| Population | Eurostat `demo_pjan` | API open data | Même producteur que le marché | Valeurs récentes « provisoires » |
| Communes allemandes | Destatis, *Gemeindeverzeichnis* 31.12.2025 | Fichier open data | Office statistique allemand : code officiel, population, coordonnées | Coordonnées du centre de la commune |
| Magasins CECONOMY | Plans de site mediamarkt.de et saturn.de | Scraper (fichiers publiés pour les robots, robots.txt respecté) | Seule liste publique complète. Recoupée avec le rapport annuel : 394 magasins trouvés contre 403 publiés | 2 % d'écart ; conditions d'utilisation des sites non lues |
| Chiffres CECONOMY | CECONOMY, *Annual Report 2024/25* | Rapport officiel | Comptes publiés d'une société cotée | Ventes Allemagne avec l'électroménager ; exercice clos au 30/09 |
| Autres concurrents | Expert, Euronics, Amazon, Otto (Conrad et Medimax en veille) | Pages officielles / rapports | Comptages nationaux, formats complémentaires | Pas de géolocalisation magasin ; ne pas additionner avec CECONOMY |
| Chiffres de la Fnac | Fnac Darty, *Document d'enregistrement universel 2025* (déposé à l'AMF) | Rapport officiel | Document réglementaire d'une société cotée | La Fnac seule n'est pas publiée : chiffres du groupe |
| TVA | Commission européenne, *Your Europe* | Page officielle | Taux publiés par la Commission | Page possiblement pas à jour |
| Droits de douane | EUR-Lex, TFUE art. 28 et 30 | Texte de loi | Interdiction des droits de douane entre pays de l'UE | — |
| Réglementation du livre | *Buchpreisbindungsgesetz*, § 3 (gesetze-im-internet.de) | Texte de loi | Prix du livre fixé par la loi | — |
| Loyer commercial | IHK Region Stuttgart, enquête 2024 | Enquête d'une chambre de commerce | Seule donnée publique accessible | **Hypothèse** : une seule ville, unité de temps (mois) déduite |
| Hub logistique | Communiqué Fnac Darty (Chilly-Mazarin) + API Découpage administratif (geo.api.gouv.fr) | Officiel | Seul site logistique confirmé publiquement | Les 7 autres plateformes ne sont pas publiées |
| Part du catalogue éligible | — | **Base interne simulée** | Aucune donnée publique | Simulée et signalée comme telle |

**Le paysage concurrentiel allemand**

| Enseigne | Groupe | Canal | Points de vente | Rôle / positionnement | Source |
|---|---|---|---|---|---|
| MediaMarkt + Saturn | CECONOMY | magasins | 394 (sitemaps) ; 403 (rapport) | Leader tech, grandes surfaces | Sitemaps + CECONOMY 2024/25 |
| Expert | Expert SE | magasins | > 400 | Réseau coopératif de proximité | expert.de, *Daten und Fakten* |
| Euronics | Euronics Deutschland eG | magasins | > 1 100 | Coopérative, petits et moyens magasins | euronics.de, *Über EURONICS* |
| Amazon.de | Amazon | en ligne | 0 | Leader de l'e-commerce | amazon.de |
| Otto.de | Otto Group | en ligne | 0 | Vente à distance et marketplace | ottogroup.com |

Les comptages ne sont pas additifs : les formats et les surfaces diffèrent. Seul CECONOMY est géolocalisé au magasin près, donc seul réseau utilisé dans le KPI de densité par Land ; les autres servent de borne de pression concurrentielle. Conrad (4 sites, surtout B2B), Electronic Partner / Medimax et les enseignes alimentaires (Kaufland, etc.) restent des acteurs de niche ou non spécialistes, non retenus dans le comptage.

**Sources écartées, et pourquoi**
- OpenStreetMap : ses serveurs n'ont pas répondu (5 essais, 2 serveurs).
- Chiffres GfK (marché français par rayon, cités par Fnac Darty) : ils auraient contredit Eurostat, la source déjà choisie pour le marché.
- Baromètre national des loyers de l'IVD : payant.
- Thalia (livres) et comparaison des 27 pays de l'UE : hors du guide des KPI, qui parle d'« un concurrent » et de « pays cible vs France ».

### 3.3 Organisation des fichiers

```
data/manual/   Chiffres relevés à la main et concurrents (source + lien)
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

### Répartition des rôles

Chaque membre est responsable de ses KPI de bout en bout, de la donnée au texte, et d'une partie transverse.

| Membre | KPI | Partie transverse |
|---|---|---|
| Romane LONG | Prix & marges ; délai de retour sur investissement (synthèse Go / No-Go) | Modèle de données (Gold), README, intégration Git |
| Samantha ASDRUBAL | Marché & potentiel : croissance, part de marché en France, pénétration | Pipeline de collecte, brique IA, stack technique |
| Arquam EL MEZOUARI EL GLAOUI | Concurrence ; réseau & implantation ; logistique & taxes | Recherche documentaire, choix des sources |
| Elena KERVENNIC | Assortiment (% du catalogue éligible) | Dashboard, slides de l'oral |

### Méthodologie

- **Les 5 étapes du cours** : compréhension métier (question du Comex, KPI) → compréhension des données (sources, fiabilité) → préparation (Bronze → Silver) → modélisation (Gold, étoile / flocon) → dataviz & déploiement.
- **Git** : une branche `feature/*` par chantier, fusionnée dans `develop` pour tester le pipeline complet, puis dans `main` une fois validée.
- **Règles d'équipe** : une source par sujet ; tout chiffre a sa source et sa page ; toute hypothèse est écrite comme telle.

### Roadmap

| Quand | Étapes | État |
|---|---|---|
| Mer. 11/11 | Cadrage, choix du pays, KPI, sources, collecte, nettoyage, modèle de données, dictionnaire | ✅ |
| Jeu. 12/11, après-midi | Gold, calcul des KPI, dashboard, brique IA, fin du README | ⬜ |
| Ven. 13/11 | Slides, répétition de l'oral, rendu à 15h | ⬜ |

### Next Steps (recommandations post-étude)

**Décision : Go sous conditions — un magasin pilote à Cologne, pas un réseau national.**

Tous les chiffres ci-dessous viennent de `data/gold/kpi.csv` (2025, sauf mention).

**Ce qui pousse au Go**
- Un marché qui grandit : dépenses TECH **+2,9 % en Allemagne** contre **−1,3 % en France** ; **363 €** par habitant contre **204 €** (pénétration 178, France = 100).
- Pas de barrière réglementaire : droits de douane **0 %**, TVA presque identique (19 % contre 20 % pour TECH).
- Cologne : Land (Rhénanie-du-Nord-Westphalie) où la densité CECONOMY est parmi les plus faibles (**4,0 magasins par million d'habitants**, moyenne nationale 4,7), et ville de plus de 500 000 habitants la plus proche du hub de Chilly-Mazarin (**416 km**, contre **619 km** en moyenne pondérée pour les 79 villes de plus de 100 000 habitants).

**Ce qui empêche un Go sans condition**
- Prix TECH **18 % plus bas** en Allemagne (indice hors taxes 82, France = 100) : à coût d'achat français, la marge brute tombe à **12 %** contre **28 %** pour le groupe.
- Concurrent installé : CECONOMY détient **17 à 38 %** du marché TECH (HT / HT), avec 394 magasins géolocalisés (403 publiés) ; Expert, Euronics, Amazon et Otto en plus.
- Délai de retour sur investissement d'un magasin de 2 400 m² : **jamais** dans 3 scénarios sur 4. Seul le scénario « achats locaux + loyer au niveau français » est rentable : **+0,45 M€ par an, 7,9 ans** *(estimation ; l'investissement de 1 500 €/m² est une hypothèse non sourcée)*.
- **Limites du ROI** : c'est un ordre de grandeur calculé avec des ratios du **groupe** (CA France, surfaces France y compris Nature & Découvertes, coûts groupe), pas de la Fnac seule ; il ne compte ni montée en charge, ni impôts, ni besoin en fonds de roulement, ni investissement de maintien. Sensibilité du scénario D (`K12_sensibilite`) : de **4,4 ans** (CA +20 %, 1 000 €/m²) à **13,2 ans** (CA −20 %, 2 000 €/m²).
- Écart à expliquer : Eurostat donne **350 € par habitant** de dépenses « journaux, livres et papeterie » en Allemagne contre **155 €** en France (2025). Les autres pays vérifiés en 2023 sont plus proches de la France (Italie, Espagne) : la différence peut venir des méthodes nationales et n'est pas utilisée comme argument.

**Conditions de succès du pilote** (issues du modèle, à valider par le Comex)
1. **Acheter en Allemagne** (centrale d'achat locale) pour retrouver une marge brute proche de **28 %**.
2. **Loyer inférieur à 33 €/m²/mois** : au-delà, le magasin perd de l'argent même avec des achats locaux. Le loyer de référence IHK (115 €/m²/mois, petites surfaces de centre-ville) est trois fois trop élevé : il faut viser un emplacement de grande surface hors rue prime.
3. **Assortiment ciblé** : produits techniques et jeux vidéo (environ 90 % éligibles), peu de livres (10 % éligibles, catalogue en français) *(données simulées)*.

| Étape | Action | Horizon | Critère de passage |
|---|---|---|---|
| 1 | Négocier une centrale d'achat allemande | M1–M6 | Marge brute TECH proche de 28 % |
| 2 | Trouver un emplacement à Cologne (2 400 m²) | M1–M6 | Loyer < 33 €/m²/mois |
| 3 | Tester la logistique : livraison depuis Chilly-Mazarin contre un prestataire allemand | M3–M6 | Coût et délai comparés (seuils à fixer) |
| 4 | Ouvrir le magasin pilote, assortiment TECH + jeux | M12 | Ouverture dans le budget (3,6 M€, hypothèse) |
| 5 | Décision de déploiement après **2 ans d'exploitation** | M36 | Résultat annuel positif et délai de retour ≤ 8 ans ; sinon arrêt |

**Arbitrages**
- **Pas de déploiement national** avant la preuve du pilote.
- **Pas de guerre des prix** : Amazon et MediaMarkt sont plus gros ; la Fnac doit se différencier par l'assortiment, le conseil et les services.
- **Pas d'acquisition de CECONOMY** : coût, endettement et risque d'exécution trop élevés pour un premier pas.

**Risques à surveiller**

| Risque | Impact | Mitigation |
|---|---|---|
| Compression de marge | Économie du modèle | Conditions d'achat, mix livres/services, prix local |
| Concurrence Amazon / MediaMarkt | Parts de marché | Différenciation, expérience en magasin, click & collect |
| Logistique depuis la France | Délai et coût | 3PL allemand, stock avancé, test comparatif |
| Réglementation et droit du travail | Ouverture | Conseil local, TVA, Buchpreisbindung, emballage |
| Exécution du pilote | Go / No-Go | Jalons, budget de sortie, critères d'arrêt écrits |

## 5. Stack technique

| Étape | Outil |
|---|---|
| Langage | Python 3.15 |
| Collecte | `urllib` (bibliothèque standard), en HTTPS avec vérification des certificats (`certifi`) |
| Nettoyage et modélisation | `pandas` 3.1.1 ; `openpyxl` 3.1.5 pour lire le fichier Excel de Destatis |
| Schémas | `matplotlib` 3.11.2 |
| Versionnement et collaboration | Git et GitHub (branches `feature/*` → `develop` → `main`) |
| Formats | JSON (Eurostat), XLSX (Destatis), XML (plans de site), CSV (Silver, Gold, chiffres relevés à la main), PPTX / HTML (restitution), JSON (commentaires IA) |
| Restitution et brique IA | `python-pptx` 1.0.2 (slides générées) ; HTML + SVG sans bibliothèque (dashboard) ; Claude en ligne de commande (`claude -p`, synthèse et commentaires), avec repli sur un texte déterministe |

### 5.1 Restitution

Deux supports, générés par le pipeline à partir du Gold (aucun chiffre saisi à la main) :

**Slides générées automatiquement** (`docs/Comex_Fnac_Allemagne.pptx`, script `src/restitution/build_slides.py`, `python-pptx`) : 9 slides au template homogène, graphiques natifs modifiables, calées sur les 5 sections de l'oral (entreprise, base de données, KPI, analyse, Go / No-Go) + une slide de réserve sur les limites. Le texte à dire est dans les notes de présentation et dans `docs/script_oral.md`, minuté.

**Dashboard interactif** (`docs/dashboard.html`, script `src/restitution/build_dashboard.py`), publié comme page claude.ai pour l'IA en direct :
- 12 onglets, une question par onglet, dans l'ordre du raisonnement : marché, prix et marges, concurrence, où ouvrir (7 villes candidates), logistique, assortiment, rentabilité, capacité financière de Fnac Darty, décision, définitions des KPI, IA et méthode.
- Filtres : ville candidate, catégorie, achats (France / Allemagne), loyer (IHK / niveau France). Chaque onglet n'affiche que les filtres qui le changent ; un test automatique vérifie que chaque filtre affiché modifie bien les chiffres, les graphiques et la demande faite à l'IA (12 onglets × 56 combinaisons, 0 erreur).
- Chaque chiffre porte une ligne « ℹ » qui dit ce qu'il mesure (moyenne, calcul, exemple), son étiquette (mesuré, estimation, hypothèse, simulé) et la source sous chaque graphique.
- Simulateur « et si… ? » (loyer, investissement, ventes) et détail du calcul du résultat d'un magasin étape par étape.

Réponses préparées aux questions du jury : `docs/questions_jury.md`.

### 5.2 Brique IA

**Principe : l'IA ne calcule rien, elle commente en direct des chiffres déjà calculés.**

1. Chaque onglet du dashboard calcule ses chiffres selon les filtres choisis.
2. Il envoie à Claude uniquement ces faits et une consigne (2 à 3 phrases pour un décideur, sans nouveau chiffre). Le prompt est visible dans la page (« Voir ce qu'on envoie à Claude »).
3. Claude répond en direct, via la capacité « sample » des pages claude.ai : rien n'est pré-écrit ni stocké dans le dépôt.
4. La page vérifie chaque nombre de la réponse : un nombre absent des faits est surligné ⚠.
5. Hors de claude.ai (fichier ouvert en local), ou si l'accès à Claude est refusé, un texte calculé sans IA s'affiche, signalé comme tel.

Pour les slides (fichier statique), `src/ai/synthese.py` et `src/ai/commentaires_dashboard.py` appellent `claude -p` au moment de générer le PowerPoint ; leurs textes sont produits localement et ne sont pas versionnés.

### 5.3 Installation et lancement

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python run_pipeline.py      # collecte, nettoyage, modèle Gold et KPI
PYTHONPATH=src .venv/bin/python src/ai/synthese.py   # brique IA (claude -p) ; --sans-ia pour le texte déterministe
PYTHONPATH=src .venv/bin/python src/ai/commentaires_dashboard.py   # commentaires IA par filtre, puis relancer run_pipeline.py
.venv/bin/python src/make_schemas.py  # schémas du README
```

---

## Sources citées

- **DEU 2024** : Fnac Darty, *Document d'enregistrement universel 2024*. https://fnacdarty.com/wp-content/uploads/2025/03/fnac-darty-deu-2024-assemblage-mel-opti.pdf
- **DEU 2025** : Fnac Darty, *Document d'enregistrement universel 2025*, déposé à l'AMF le 06/03/2026. https://www.fnacdarty.com/wp-content/uploads/2026/03/fnac-darty-deu-2025-assemblage-pdf-opti-1.pdf
- **Fnac Darty around the world** : https://www.fnacdarty.com/en/group/fnac-darty-around-the-world/
- **Eurostat `demo_pjan`** : population au 1er janvier. https://ec.europa.eu/eurostat/databrowser/view/demo_pjan/default/table
- **Eurostat `nama_10_cp18`** : dépenses des ménages par fonction (COICOP 2018). https://ec.europa.eu/eurostat/databrowser/view/nama_10_cp18/default/table
- **Eurostat `prc_ppp_ind_1`** : indices de niveau des prix. https://ec.europa.eu/eurostat/databrowser/view/prc_ppp_ind_1/default/table
- **Destatis** : *Gemeindeverzeichnis*, 31.12.2025. https://www.destatis.de/DE/Themen/Laender-Regionen/Regionales/Gemeindeverzeichnis/Administrativ/Archiv/GVAuszugJ/31122025_Auszug_GV.xlsx?__blob=publicationFile
- **CECONOMY** : *Annual Report 2024/25*. https://www.ceconomy-mms.com/api/documents/file/CECONOMY%20Annual%20Report%202024-25
- **Commission européenne** : *VAT rates*. https://ec.europa.eu/youreurope/business/taxation/vat/vat-rules-rates/index_en.htm
- **EUR-Lex** : TFUE, art. 28 et 30 (union douanière). https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=LEGISSUM:customs_union
- **Buchpreisbindungsgesetz** : § 3. https://www.gesetze-im-internet.de/buchprg/__3.html
- **IHK Region Stuttgart** : *Mietpreisumfrage Einzelhandel 2024*. https://www.ihk.de/stuttgart/branchen/handel/zahlen-und-fakten/mietpreisumfrage-einzelhandel-2024-6201604
- **Fnac Darty** : communiqué de la plateforme de Chilly-Mazarin. https://www.fnacdarty.com/en/inauguration-of-a-new-platform-dedicated-to-deliveryand-after-sales-service-in-chilly-mazarin/
- **Expert SE** : *Daten und Fakten*. https://www.expert.de/Pressemitteilungen/Daten-Fakten
- **Euronics Deutschland eG** : *Über EURONICS*. https://www.euronics-deutschland.de/ueber-euronics/
- **Amazon.de** : https://www.amazon.de/
- **Otto Group** : https://www.ottogroup.com/en/
