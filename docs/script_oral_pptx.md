# Script de l'oral (10 min)

Généré par `src/restitution/build_slides.py` avec les chiffres du Gold. Le même texte est dans les notes de présentation du PowerPoint. Répartition Romane / Elena proposée, à ajuster.

## Slide 1 · COMEX FNAC · STRATÉGIE 2027-2029
**0:00 → 0:15 · Romane**

Bonjour. Le Comex de la Fnac nous pose une seule question : l'implantation en Allemagne est-elle réalisable et rentable ? On a construit toute la chaîne de données pour y répondre ; notre décision arrive à la fin.

## Slide 2 · Une Fnac qui rétrécit en France, un marché allemand qui grandit
**0:15 → 1:00 · Romane**

La Fnac compte 205 magasins en France fin 2025, après 15 fermetures. Les dépenses des ménages allemands en tech progressent de 2,7 % par an depuis 2015, quand elles reculent de 0,8 % en France. L'Allemagne est le premier marché d'Europe et le groupe n'y a aucun magasin.

## Slide 3 · Un pipeline simple, des sources officielles,
des chiffres traçables
**1:00 → 2:30 · Elena**

Aucune donnée n'était fournie : tout vient de sources publiques. On a utilisé l'API d'Eurostat, l'office statistique de l'Union européenne, pour le marché, les prix et la population ; le fichier officiel allemand des communes ; et du scraping pour localiser les magasins MediaMarkt et Saturn, à partir des plans de site publiés pour les robots. Le pipeline suit les trois couches du cours : Bronze, Silver, Gold ; le modèle de données est détaillé dans le README. Chaque chiffre porte son étiquette : mesuré, estimation, hypothèse ou simulé.

## Slide 4 · Un KPI par question du Comex, un KPI de synthèse pour trancher
**2:30 → 4:30 · Romane**

On a suivi le guide des KPI du Comex, axe par axe, en se demandant pour chacun quelle décision il éclaire. Aucun ne répond seul à « rentable ? » : on a donc ajouté un KPI de synthèse, le délai de retour d'un magasin, et le cash-flow du groupe pour savoir s'il peut financer le projet. Méthode : on compare toujours hors taxes, et chaque KPI a sa définition en clair dans le dashboard.

## Slide 5 · Un Allemand dépense 1,8 fois plus en tech qu'un Français
**4:30 → 5:15 · Elena**

Premier constat : le marché attire. Un Allemand dépense 363 euros par an en tech, un Français 204, et l'écart se creuse depuis 2015. Mais la place est prise : CECONOMY, c'est-à-dire MediaMarkt et Saturn, tient entre 17 et 38 % du marché, et deux coopératives, Expert et Euronics, ont des centaines de petits magasins.

## Slide 6 · Mais la France est plus chère : vendre au prix allemand écrase la marge
**5:15 → 6:00 · Romane**

Deuxième constat, et c'est la réponse à une question qu'on nous pose souvent : non, la France n'est pas moins chère. Les produits tech y coûtent 116,5 contre 94,7 en Allemagne, sur une base 100 européenne. Si la Fnac achète au prix français et vend au prix allemand, sa marge tombe à 12,2 %, contre 28 %. Il n'y a aucun droit de douane entre les deux pays : la difficulté est économique, pas réglementaire.

## Slide 7 · Où ouvrir ? Cologne coche les 3 critères
**6:00 → 6:45 · Elena**

Troisième question : où ouvrir. On ne regarde que les 7 plus grandes villes, celles qui peuvent faire vivre un grand magasin, et on les note sur trois critères simples. Cologne est la seule à cocher les trois : plus d'un million d'habitants, peu de magasins du concurrent pour sa taille, et 416 km de notre entrepôt. Un entrepôt en Allemagne diviserait les distances par deux, mais pour un seul magasin, livrer depuis la France suffit. [DÉMO 30 s : dashboard, onglet « Où ouvrir ? », changer de ville ; le commentaire IA se réécrit en direct]

## Slide 8 · Un magasin n'est rentable qu'avec des achats en Allemagne et un loyer maîtrisé
**6:45 → 7:30 · Romane**

Le cœur de l'analyse : on a calculé le résultat d'un magasin de 2 400 m² dans quatre scénarios, achats en France ou en Allemagne, loyer de centre-ville ou au niveau français. Trois sur quatre perdent de l'argent. Seul le scénario achats allemands et loyer maîtrisé gagne 0,45 M€ par an, soit un retour en 7,9 ans. L'encadré violet est écrit par notre brique IA : elle ne calcule rien, elle commente nos KPI, et un script vérifie chaque chiffre qu'elle écrit.

## Slide 9 · La Fnac peut financer un pilote, pas un réseau
**7:30 → 8:00 · Elena**

Dernière question : le groupe a-t-il les moyens ? le groupe Fnac a dégagé 145 millions d'euros de cash-flow libre en 2025 ; le pilote en coûte 3,6, soit 2,5 %. Mais le résultat net est négatif, -145,6 M€ : on peut financer un test, pas un déploiement national.

## Slide 10 · 5 · DÉCISION ET RECOMMANDATION · DÉFENSE DES ARBITRAGES 15 PTS
**8:00 → 9:30 · Romane**

Notre décision : Go sous conditions, pour un seul magasin pilote à Cologne, pas un réseau. Trois conditions : acheter en Allemagne pour retrouver notre marge ; un loyer sous 33 euros le mètre carré ; un assortiment centré sur la tech et les jeux vidéo. Cologne est la seule grande ville qui coche nos trois critères. Calendrier : centrale d'achat et bail dans les six premiers mois, ouverture à un an, décision de déploiement à trois ans, avec un critère d'arrêt écrit.

## Slide 11 · 5 · DÉCISION ET RECOMMANDATION
**9:30 → 10:00 · Romane**

Concrètement, nous demandons au Comex trois décisions : valider le pilote de Cologne, valider nos trois conditions, et fixer dès maintenant le rendez-vous de décision à trois ans avec un critère d'arrêt. Merci, nous sommes prêts pour vos questions.

## Slide 12 · Comment on a utilisé l'IA, et nos limites
**réserve · Romane + Elena**

Slide de réserve. Si on nous demande comment on a utilisé l'IA : elle ne calcule rien ; elle reçoit nos chiffres et les commente en direct, et la page vérifie chaque nombre. Si le jury attaque le ROI : c'est un ordre de grandeur, et la sensibilité montre que la conclusion tient : il faut des achats locaux et un loyer maîtrisé dans tous les cas.
