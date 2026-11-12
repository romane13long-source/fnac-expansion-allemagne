# Script de l'oral : Fnac → Allemagne (10 min)

Présentation : `docs/slides.html` (F = plein écran, flèches = avancer, N = notes sous la slide). PDF : `docs/Comex_Fnac_Allemagne.pdf`.
Minutage calé sur le tableau de l'oral du sujet. Répartition Romane / Elena proposée, à ajuster.
Tous les chiffres viennent du repo (`data/gold/kpi.csv`, sources citées sur chaque slide et en slide 13).

| Section du sujet | Temps | Slides | Qui |
|---|---|---|---|
| 1. Entreprise et pays cible | 1 min | 1-2 | Romane |
| 2. Base de données et cadrage | 1 min 30 | 3 | Elena |
| 3. Démarche analytique | 2 min | 4 | Romane |
| 4. Analyse et brique IA | 3 min | 5-9 | Elena / Romane en alternance |
| 5. Décision et recommandation | 1 min 30 | 10-11 | Romane |
| Questions | — | 12 (définitions), 13 (sources) | les deux |

---

## Slide 1 · Couverture — 0:00 → 0:10 · Romane

> Bonjour. Le Comex de la Fnac nous pose une question : s'implanter en Allemagne, est-ce réalisable et rentable ? Notre réponse arrive en fin de présentation.

## Slide 2 · La Fnac recule en France, le marché allemand progresse — 0:10 → 1:00 · Romane

> En France, la Fnac compte 205 magasins fin 2025, après 15 fermetures dans l'année : le réseau se contracte.
> L'Allemagne, c'est 83,6 millions d'habitants, le premier marché d'Europe. Les dépenses tech y progressent de 2,7 % par an depuis 2015, alors qu'elles reculent de 0,8 % par an en France.
> La Fnac n'y a aucun magasin. Le leader local, MediaMarkt-Saturn, est déjà notre concurrent en France. L'enjeu de 2027-2029 : trouver de la croissance hors de France sans détruire de valeur.

*Transition :* « Pour répondre, il nous fallait des données fiables. Elena. »

## Slide 3 · Des données publiques, fiables et traçables — 1:00 → 2:30 · Elena

> Aucune donnée n'était fournie : tout vient de sources publiques.
> Eurostat, l'office statistique européen, via son API, pour le marché, les prix et la population. Destatis pour les communes allemandes. Pour les magasins du concurrent, du scraping : on a lu les plans de site de MediaMarkt et Saturn et localisé 394 magasins. Les chiffres d'entreprise viennent des rapports annuels.
> Tout passe par un pipeline en trois couches : Bronze, la donnée brute ; Silver, une table propre par source ; Gold, un modèle en étoile, avec un flocon de la commune vers le Land. Un seul script refait toute la chaîne.
> Chaque chiffre est étiqueté : mesuré, estimation, hypothèse ou simulé. Le détail des sources est en annexe.

*Transition :* « Avec ces données, quels indicateurs suivre ? Romane. »

## Slide 4 · Un indicateur pour chaque question du Comex — 2:30 → 4:30 · Romane

> Le sujet proposait une douzaine d'indicateurs. On en a retenu neuf, avec une règle simple : une question précise du Comex, un indicateur qui y répond, et une source fiable pour le calculer.
> Le marché attire-t-il ? La croissance du secteur et la part de marché du leader allemand.
> Notre prix tient-il ? L'indice de prix Allemagne-France et la marge brute.
> Où ouvrir, à quel coût ? La densité de magasins concurrents et le coût au mètre carré.
> Peut-on livrer ? La distance à notre entrepôt et le coût du transport.
> Que vendre ? La dépense par habitant, catégorie par catégorie.
> Et comme aucun ne répond seul à « est-ce rentable ? », un indicateur de synthèse : le délai de retour sur investissement d'un magasin.
> On en a écarté trois : la part de marché de la Fnac en France, qui décrit la France et pas l'Allemagne ; la douane et la TVA, sans effet sur la décision ; et la part du catalogue vendable, parce que la donnée est simulée.

*Transition :* « Voici ce que disent les chiffres. Elena. »

## Slide 5 · Un marché attractif : 1,8 fois plus de dépenses tech par habitant — 4:30 → 5:00 · Elena

> Premier constat : le marché attire. Un Allemand dépense 363 euros par an en tech, un Français 204 : 1,8 fois plus, et l'écart se creuse depuis 2015.
> Mais la place est prise : le leader tient entre 17 et 38 % du marché, et deux réseaux, Expert et Euronics, ont des centaines de magasins. Il faudra se différencier.

## Slide 6 · Des prix 18 % plus bas : il faut acheter en Allemagne — 5:00 → 5:35 · Romane

> Deuxième constat, contre-intuitif : la tech est moins chère en Allemagne. Sur un même panier, la France est à 116,5, l'Allemagne à 94,7, sur une base 100 européenne. Hors TVA, l'écart est de 18 %.
> Si la Fnac achète au prix français et revend au prix allemand, sa marge brute tombe de 28 % à 12 %. C'est un ordre de grandeur : un prix moyen national, pas nos prix réels, et on suppose le même coût d'achat. Mais le sens est clair : il faut acheter en Allemagne.

## Slide 7 · Un magasin rentable à deux conditions : achats locaux et loyer modéré — 5:35 → 6:15 · Elena

> Troisième constat, le plus important. On a simulé un magasin type de 2 400 mètres carrés, avec 14,6 millions d'euros de ventes par an, et calculé ce qu'il gagne après les produits, les salaires et le loyer.
> On a croisé deux choix. Où acheter les produits : en France ou en Allemagne. Quel loyer : celui d'un centre-ville allemand, 115 euros le mètre carré par mois, ou un loyer modéré, au niveau de ce que paie la Fnac en France.
> Résultat : trois cas sur quatre perdent de l'argent. Un seul est rentable : achats en Allemagne et loyer modéré, 0,45 million par an. L'ouverture, 3,6 millions, est remboursée en 7,9 ans.
> Le seuil à retenir : au-delà de 33 euros le mètre carré, le magasin perd de l'argent. Il faut donc éviter les rues les plus chères.

## Slide 8 · Cologne, la ville la plus adaptée pour un magasin pilote — 6:15 → 6:50 · Romane

> Où ouvrir ? On a comparé les sept plus grandes villes allemandes sur trois critères : plus d'un million d'habitants, peu de magasins du leader pour leur taille, et moins de 450 kilomètres de notre entrepôt.
> Cologne est la seule à cocher les trois. Elle est à 416 kilomètres de notre entrepôt de Chilly-Mazarin, en Essonne.
> Mais livrer depuis la France a un coût : un camion par semaine, c'est 0,08 à 0,09 million d'euros par an, et le retour sur investissement passerait de 7,9 à près de 10 ans. C'est une hypothèse prudente, mais elle suffit à trancher : la tech doit être livrée par des fournisseurs allemands. L'entrepôt en Allemagne sera étudié si on déploie.

## Slide 9 · L'IA commente nos chiffres, elle ne les calcule pas — 6:50 → 7:30 · Elena

> Notre brique IA. Les calculs restent dans notre code. Le dashboard calcule les indicateurs selon les filtres ; Claude reçoit uniquement ces chiffres et rédige deux ou trois phrases pour un décideur. Un script vérifie ensuite que chaque nombre écrit existe dans nos données.
> Quand on change un filtre, le commentaire change : 109 situations. Exemple, le même magasin à Cologne : achats en France et loyer de centre-ville, l'IA explique qu'on perd 4,1 millions par an ; achats en Allemagne et loyer modéré, qu'on gagne 0,45 million et qu'on rembourse en 7,9 ans.

*Transition :* « Donc, réalisable et rentable ? Romane. »

## Slide 10 · Décision — 7:30 → 9:00 · Romane

> Réponse au Comex. Réalisable ? Oui : marché porteur, pas d'obstacle réglementaire, une ville identifiée et des fournisseurs sur place. Rentable ? Oui, mais seulement sous trois conditions.
> Notre décision : Go sous trois conditions, pour un seul magasin pilote à Cologne.
> Un : acheter et se faire livrer en Allemagne, pour garder 28 % de marge au lieu de 12, sans payer de camions depuis la France. Deux : un loyer sous 33 euros le mètre carré. Trois : la tech d'abord, où un Allemand dépense 1,8 fois plus qu'un Français.
> Next steps : centrale d'achat et bail dans les six premiers mois ; un test de livraison, fournisseurs allemands contre camion depuis la France ; ouverture à un an ; décision de déploiement à trois ans.
> Critère d'arrêt : si le magasin perd de l'argent, ou rembourse en plus de huit ans, on ne déploie pas.

## Slide 11 · Nos demandes au Comex — 9:00 → 9:30 · Romane

> Nous demandons trois décisions : valider le pilote de Cologne, valider nos trois conditions, et fixer dès aujourd'hui le rendez-vous de décision à trois ans.
> Merci, nous sommes prêts pour vos questions.

---

## Pour les questions (slides 12-13 et `docs/questions_jury.md`)

**Slide 12 · Définition des indicateurs** : à afficher si le jury demande comment un KPI est calculé.

**Slide 13 · Sources et méthode de collecte** : à afficher pour « d'où viennent les chiffres ? » ou « comment avez-vous scrapé ? ».

**Le groupe peut-il financer ? (oral, pas de slide)** 145 millions d'euros de cash-flow libre en 2025 ; le pilote en coûte 3,6, soit 2,5 %. Mais le résultat net 2025 est de −145,6 millions : on peut financer un test, pas un réseau. Chiffres publiés pour l'ensemble du groupe.

**Nos limites, à dire si on nous les demande :**
- La rentabilité est un ordre de grandeur : ratios du groupe, sans montée en charge ni impôts. Selon les ventes et l'investissement, le retour va de 4,4 à 13,2 ans ; la conclusion ne change pas.
- L'investissement de 1 500 € par m², le loyer de 115 € et le coût du camion (1,45 à 1,67 € par km, calculateur privé citant le CNR) sont des hypothèses.
- La part du catalogue vendable est simulée : c'est pour ça qu'on l'a écartée des KPI de décision.
- On a trouvé 394 magasins du concurrent contre 403 publiés.

**Questions probables :**
- *« Pourquoi ces 9 KPI et pas les autres ? »* Une question précise, un indicateur, une source fiable (méthode du cours). On a écarté ce qui ne change pas la décision (douane, TVA, part de la Fnac en France) et ce dont la donnée est simulée (catalogue).
- *« Le transport depuis la France, combien ? »* 1 450 à 1 670 € l'aller-retour, 0,08 à 0,09 M€ par an pour un camion par semaine : le retour passerait à 9,5-9,8 ans. D'où la condition : fournisseurs allemands. C'est une borne haute, car nos ratios de coûts du groupe comprennent déjà de la logistique.
- *« Le cash-flow, ça sert à la part de marché ? »* Non : la part de marché, c'est nos ventes divisées par le marché. Le cash-flow et le résultat net disent si le groupe peut financer le projet.
- *« Eurostat, c'est fiable ? »* C'est l'office statistique de l'Union européenne : il harmonise les chiffres des instituts nationaux pour comparer les pays.
- *« Comment avez-vous fait le scraping ? »* On a lu les plans de site publiés pour les robots (robots.txt respecté), puis rattaché chaque magasin à sa commune ; les villes homonymes ont été corrigées à la main.
- *« C'est quoi le loyer modéré ? »* Le poids des loyers dans le chiffre d'affaires de la Fnac en France, appliqué au magasin de Cologne.
- *« Pourquoi seulement 7 villes ? »* Ce sont les seules assez grandes pour faire vivre un magasin de 2 400 m².
- *« Pourquoi pas un entrepôt en Allemagne ? »* Pour un seul magasin, il coûterait plus qu'il ne rapporte ; on l'étudiera si on déploie.
- *« Et si l'IA se trompe ? »* Elle ne calcule rien, et un script vérifie chaque nombre qu'elle écrit ; un nombre inconnu est rejeté.
