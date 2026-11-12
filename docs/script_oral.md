# Script de l'oral : Fnac → Allemagne (10 min)

Présentation : `docs/slides.html` (F = plein écran, flèches = avancer, N = afficher ces notes sous la slide).
Le minutage suit le tableau de l'oral du sujet (slide 8 du PDF). Répartition Romane / Elena proposée, à ajuster.
Tous les chiffres viennent du repo (`data/gold/kpi.csv` et sources citées sur chaque slide).

| Section du sujet | Temps | Slides | Qui |
|---|---|---|---|
| 1. Entreprise et pays cible | 1 min | 1-2 | Romane |
| 2. Base de données et cadrage | 1 min 30 | 3 | Elena |
| 3. Démarche analytique | 2 min | 4 | Romane |
| 4. Analyse et brique IA | 3 min | 5-9 | Elena / Romane en alternance |
| 5. Décision et recommandation | 1 min 30 | 10-11 | Romane |
| Questions | — | annexes A-B | les deux |

---

## Slide 1 · Couverture — 0:00 → 0:10 · Romane

> Bonjour. Le Comex de la Fnac nous pose une seule question : l'implantation en Allemagne est-elle réalisable et rentable ? Nous allons y répondre en dix minutes, et notre décision arrive à la fin.

## Slide 2 · La Fnac recule en France, le marché allemand grandit — 0:10 → 1:00 · Romane

> La Fnac compte 205 magasins en France fin 2025, après 15 fermetures dans l'année : le réseau français se contracte.
> En face, l'Allemagne : 83,6 millions d'habitants, le premier marché d'Europe, et des dépenses tech qui progressent de 2,7 % par an depuis 2015, quand elles reculent de 0,8 % par an en France.
> La Fnac n'y a aucun magasin, et le leader local, MediaMarkt-Saturn, est déjà notre concurrent direct en France. L'enjeu de la stratégie 2027-2029, c'est donc de trouver de la croissance hors de France, sans détruire de valeur.

*Transition :* « Pour répondre, il nous fallait des données fiables. Elena. »

## Slide 3 · Une architecture solide, des sources fiables — 1:00 → 2:30 · Elena

> Aucune donnée n'était fournie : tout vient de sources publiques.
> Pour le marché, les prix et la population, on a utilisé l'API d'Eurostat, l'office statistique de l'Union européenne. Pour les villes, le fichier officiel des communes allemandes, Destatis. Pour les magasins du concurrent, on a fait du scraping : on a lu les plans de site de MediaMarkt et de Saturn, des fichiers publiés pour les robots, et on a localisé 394 magasins. Les chiffres des entreprises viennent de leurs rapports annuels, page par page.
> Tout passe par un pipeline en trois couches, comme vu en cours : Bronze, la donnée brute jamais modifiée ; Silver, une table propre par source ; Gold, un modèle en étoile avec un flocon, de la commune vers le Land. Un seul script refait toute la chaîne, et relancé deux fois il donne exactement le même résultat.
> Enfin, chaque chiffre est étiqueté : mesuré quand il est officiel, estimation quand c'est notre calcul, hypothèse quand il n'a pas de source, simulé pour les données fictives. On sait toujours d'où vient un chiffre.

*Transition :* « Avec ces données, quels indicateurs suivre ? Romane. »

## Slide 4 · Pour chaque question du Comex, un indicateur qui aide à décider — 2:30 → 4:30 · Romane

> On est partis du guide des KPI du Comex, et pour chaque indicateur on s'est demandé : quelle décision il éclaire ?
> Le marché attire-t-il ? On mesure la croissance du secteur et les parts de marché : celle de la Fnac en France, celle du leader en Allemagne. Ça donne le plafond de chiffre d'affaires.
> Notre prix tient-il ? L'indice de prix Allemagne-France et la marge brute après taxes.
> Où ouvrir, et à quel coût ? La densité de magasins concurrents et le coût au mètre carré.
> Peut-on livrer ? La distance à notre entrepôt et les taxes.
> Que vendre ? La consommation par catégorie et la part de notre catalogue vendable en Allemagne.
> Mais aucun de ces indicateurs ne répond seul à « est-ce rentable ? ». On a donc ajouté un KPI de synthèse : le délai de retour sur investissement d'un magasin, et le cash-flow du groupe pour savoir s'il peut financer le projet.

*Transition :* « Voici ce que disent les chiffres. Elena. »

## Slide 5 · Les Allemands dépensent 1,8 fois plus en tech : le marché est attractif — 4:30 → 5:00 · Elena

> Premier constat : le marché attire. Un Allemand dépense 363 euros par an en produits tech, un Français 204 : 1,8 fois plus, et l'écart se creuse depuis 2015.
> Mais la place est prise : le leader CECONOMY, c'est-à-dire MediaMarkt et Saturn, tient entre 17 et 38 % du marché, et deux coopératives, Expert et Euronics, ont des centaines de magasins. Il y a de la demande, mais il faudra se différencier.

## Slide 6 · Les prix sont 18 % plus bas en Allemagne : si on achète en France, la marge passe de 28 % à 12 % — 5:00 → 5:35 · Romane

> Deuxième constat. On pense souvent que la France est moins chère : c'est l'inverse. Sur un même panier tech, la France est à 116,5 et l'Allemagne à 94,7, sur une base 100 européenne. Une fois la TVA retirée, la tech est 18 % moins chère en Allemagne.
> Si la Fnac achète ses produits au prix français et les revend au prix allemand, sa marge brute passe de 28 % à 12 %. Et attention : avoir plus d'habitants ne change pas les prix, mais chaque Allemand achète plus. Conclusion : il faut acheter en Allemagne.

## Slide 7 · Un magasin ne gagne de l'argent que si on achète en Allemagne et que le loyer reste bas — 5:35 → 6:15 · Elena

> Troisième constat, le plus important. On a calculé ce que gagne un magasin de 2 400 mètres carrés, qui ferait 14,6 millions d'euros de ventes par an : ce qui reste après avoir payé les produits, les salaires et le loyer.
> On a croisé deux choix : acheter en France ou en Allemagne, et un loyer de centre-ville ou modéré. Trois combinaisons sur quatre perdent de l'argent. Seule la combinaison achats en Allemagne et loyer modéré gagne 0,45 million par an, et rembourse l'ouverture, 3,6 millions, en 7,9 ans.
> Le seuil à retenir : au-delà de 33 euros le mètre carré par mois, on perd de l'argent. La chambre de commerce allemande, l'IHK, donne 115 euros en centre-ville : il faut éviter les rues les plus chères.

## Slide 8 · Où ouvrir ? À Cologne, livrée depuis notre entrepôt en France — 6:15 → 6:50 · Romane

> Où ouvrir ? On a comparé les sept plus grandes villes allemandes sur trois critères simples : plus d'un million d'habitants, peu de magasins du leader pour leur taille, et moins de 450 kilomètres de notre entrepôt.
> Cologne est la seule à cocher les trois. Elle est à 416 kilomètres de notre entrepôt de Chilly-Mazarin, en Essonne : on livre le pilote depuis la France. Un entrepôt en Allemagne, à Cologne, diviserait les distances par plus de deux, mais il ne se justifie que si on déploie un réseau.

## Slide 9 · La brique de synthèse IA — 6:50 → 7:30 · Elena

> Notre brique IA. Le principe : l'IA ne calcule rien, les calculs restent dans notre code. Le dashboard calcule les indicateurs selon les filtres choisis ; Claude reçoit uniquement ces chiffres, avec une consigne : écrire deux ou trois phrases pour un décideur. Un script vérifie ensuite que chaque nombre écrit par l'IA existe bien dans nos données.
> Quand on change un filtre, le commentaire change : 109 situations au total. Exemple ici, le même magasin à Cologne : avec des achats en France et un loyer de centre-ville, l'IA explique qu'on perd 4,1 millions par an ; avec des achats en Allemagne et un loyer modéré, qu'on gagne 0,45 million et qu'on rembourse en 7,9 ans.

*Transition :* « Donc, réalisable et rentable ? Romane. »

## Slide 10 · Décision — 7:30 → 9:00 · Romane

> Réponse à la question du Comex. Réalisable ? Oui : le marché est porteur, il n'y a pas d'obstacle réglementaire, et on a identifié la ville et l'entrepôt. Rentable ? Oui, mais seulement sous trois conditions ; sinon, le magasin perd de l'argent.
> Notre décision est donc : Go, sous trois conditions, pour un seul magasin pilote à Cologne.
> Un : acheter en Allemagne, pour garder 28 % de marge au lieu de 12. Deux : un loyer sous 33 euros le mètre carré, donc une grande surface hors des rues les plus chères. Trois : un assortiment tech et jeux vidéo, dont 90 % du catalogue est vendable en Allemagne.
> Next steps : dans les six premiers mois, une centrale d'achat allemande et le bail à Cologne ; en parallèle, un test de livraison depuis la France ; ouverture du pilote à un an ; décision de déploiement à trois ans.
> Et on s'engage sur un critère d'arrêt : si le magasin perd de l'argent, ou s'il met plus de huit ans à rembourser, on ne déploie pas.

## Slide 11 · Ce que nous demandons au Comex — 9:00 → 9:30 · Romane

> Concrètement, nous demandons au Comex trois décisions : valider le pilote de Cologne, valider nos trois conditions, et fixer dès aujourd'hui le rendez-vous de décision à trois ans.
> Merci, nous sommes prêts pour vos questions.

---

## Pour les questions (annexes et `docs/questions_jury.md`)

**Annexe A · Le groupe peut-il financer ?** 145 millions d'euros de cash-flow libre en 2025 ; le pilote en coûte 3,6, soit 2,5 %. Mais le résultat net 2025 est de −145,6 millions : on peut financer un test, pas un réseau. Ces chiffres sont publiés pour l'ensemble du groupe, la Fnac seule ne l'est pas.

**Annexe B · Nos limites.**
- La rentabilité est un ordre de grandeur : ratios du groupe, sans montée en charge ni impôts. Selon les ventes et l'investissement, le retour va de 4,4 à 13,2 ans ; la conclusion ne change pas : il faut acheter en Allemagne et maîtriser le loyer.
- L'investissement de 1 500 € par m² et le loyer de 115 € sont des hypothèses.
- La part du catalogue vendable est simulée : le catalogue de la Fnac n'est pas public.
- On a trouvé 394 magasins du concurrent contre 403 publiés.

**Questions probables :**
- *« Eurostat, c'est fiable ? »* C'est l'office statistique de l'Union européenne : il harmonise les chiffres des instituts nationaux pour qu'on puisse comparer les pays.
- *« Comment avez-vous fait le scraping ? »* On a lu les plans de site publiés pour les robots (robots.txt respecté), puis rattaché chaque magasin à sa commune ; les villes homonymes ont été corrigées à la main.
- *« Pourquoi seulement 7 villes ? »* Ce sont les seules assez grandes pour faire vivre un magasin de 2 400 m².
- *« Pourquoi pas un entrepôt en Allemagne ? »* Pour un seul magasin, l'entrepôt coûterait plus qu'il ne rapporte ; on l'étudiera si on déploie.
- *« Que se passe-t-il si l'IA se trompe ? »* Elle ne calcule rien, et un script vérifie chaque nombre qu'elle écrit ; un nombre inconnu est rejeté.
