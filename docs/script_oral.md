# Script de l'oral (10 min)

Généré par `src/restitution/build_slides.py` avec les chiffres du Gold. Le même texte est dans les notes de présentation du PowerPoint. Répartition Romane / Elena proposée, à ajuster.

## Slide 1 · Titre
**0:00 → 0:20 · Romane**

Bonjour. Le Comex de la Fnac nous pose une seule question : l'implantation en Allemagne est-elle réalisable et rentable ? Pour y répondre, on a construit toute la chaîne de données, du téléchargement jusqu'à la recommandation. Notre décision arrive à la fin ; voici d'abord le contexte.

## Slide 2 · Une Fnac qui rétrécit en France, un marché allemand qui grandit
**0:20 → 1:00 · Romane**

La Fnac compte 205 magasins en France fin 2025, après 15 fermetures dans l'année. En face, les dépenses des ménages allemands en produits techniques progressent de 2,7 % par an depuis 2015, quand elles reculent de 0,8 % en France. L'Allemagne est le premier marché d'Europe, le groupe n'y a aucun magasin, et son leader MediaMarkt-Saturn est déjà notre concurrent direct. C'est donc le pays le plus logique à tester.

## Slide 3 · Un pipeline reproductible, une source officielle par sujet
**1:00 → 2:30 · Elena**

Aucune donnée n'était fournie : on a tout collecté en données publiques. Le pipeline suit les trois couches vues en cours : Bronze, la donnée brute jamais modifiée ; Silver, une table propre par source ; Gold, le modèle en étoile. On a quatre tables de faits de grains différents qui partagent leurs dimensions, avec un flocon commune vers Land pour la zone de chalandise. Côté sources, une seule source officielle par sujet, pour ne jamais afficher deux chiffres différents : Eurostat pour le marché et les prix, Destatis pour les 10 753 communes, les rapports annuels pour les entreprises. Et tout ce qui n'est pas officiel est étiqueté hypothèse ou simulé.

## Slide 4 · Un KPI par question du Comex, un KPI de synthèse pour trancher
**2:30 → 4:30 · Romane**

On a suivi le guide des KPI du Comex, axe par axe, et on s'est demandé pour chacun : quelle décision il éclaire. Le marché dit quel chiffre d'affaires est accessible. Les prix disent si notre positionnement tient. Le réseau dit où ouvrir et à quel coût. La logistique dit si on peut livrer depuis la France. L'assortiment dit si on vend tout le catalogue ou une sélection. Mais aucun de ces KPI ne répond seul à « rentable ? ». On a donc ajouté un KPI de synthèse : le délai de retour sur investissement d'un magasin, calculé à partir de tous les autres. Deux points de méthode : les parts de marché sont comparées hors taxes des deux côtés, et les prix sont comparés hors TVA.

## Slide 5 · Le marché allemand attire : deux fois plus gros et en croissance
**4:30 → 5:30 · Elena**

Premier constat : le marché attire. Les ménages allemands dépensent 363 euros par habitant en produits techniques, contre 204 en France, et la courbe monte quand la française stagne. Aucune barrière réglementaire : zéro droit de douane, une TVA quasi identique. Mais la place est prise : CECONOMY, MediaMarkt et Saturn, tient entre 17 et 38 % du marché.

## Slide 6 · Mais les prix allemands écrasent notre marge
**5:30 → 6:30 · Romane**

Deuxième constat : les produits techniques sont environ 18 % moins chers en Allemagne, hors taxes. Si la Fnac achète ses produits au prix français et les revend au prix allemand, sa marge brute tombe à 12,2 %, contre 28 % pour le groupe. C'est la première condition : il faut acheter en Allemagne, via une centrale d'achat locale. Les livres résistent mieux, mais seuls 10 % de notre catalogue de livres, en français, est vendable là-bas.

## Slide 7 · Un seul scénario rentable : achats locaux et loyer maîtrisé
**6:30 → 7:30 · Elena**

Troisième constat, le plus important. On a simulé le résultat d'un magasin de 2 400 mètres carrés dans quatre scénarios : achats en France ou en Allemagne, loyer de centre-ville ou loyer au niveau français. Trois sur quatre perdent de l'argent. Seul le scénario achats locaux et loyer maîtrisé est rentable, avec un retour en 7,9 ans. D'où la deuxième condition : un loyer sous 33 euros le mètre carré par mois. Le commentaire en violet est rédigé par notre brique IA : elle lit uniquement nos KPI, et un script vérifie que chaque chiffre qu'elle écrit existe bien dans nos données. [DÉMO, 30 s] Dans le dashboard, onglet Rentabilité : changer le filtre Loyer, le commentaire IA change ; bouger le curseur Loyer du simulateur jusqu'à 33 euros, le verdict passe au rouge.

## Slide 8 · GO SOUS CONDITIONS : un magasin pilote à Cologne
**7:30 → 9:00 · Romane**

Notre décision : Go sous conditions, pour un seul magasin pilote, pas un réseau national. Trois conditions. Un : acheter en Allemagne pour retrouver notre marge. Deux : un loyer sous 33 euros le mètre carré, donc une grande surface hors des rues commerçantes les plus chères. Trois : un assortiment ciblé sur la tech et les jeux vidéo. Pourquoi Cologne : sa région a l'une des densités concurrentes les plus faibles, 4 magasins par million d'habitants, et c'est la grande ville la plus proche de notre entrepôt, à 416 kilomètres. Calendrier : centrale d'achat et bail dans les six premiers mois, ouverture à un an, et décision de déploiement après deux ans d'exploitation, avec un critère d'arrêt écrit : si le magasin perd de l'argent ou si le retour dépasse 8 ans, on s'arrête.

## Slide 9 · Nos limites, dites avant qu'on nous les pose
**9:00 → 10:00 · Romane + Elena**

Slide de réserve pour les questions. Si le jury attaque le ROI : c'est un ordre de grandeur, on l'assume, et la sensibilité montre que la conclusion tient : il faut des achats locaux et un loyer maîtrisé dans tous les cas. Si on nous demande pourquoi pas les livres : seuls 10 % du catalogue de livres est vendable, puisqu'il est en français.
