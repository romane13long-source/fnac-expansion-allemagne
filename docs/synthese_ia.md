# Synthèse pour le Comex

*Générée par : Claude (sonnet) via claude -p, chiffres contrôlés. Source des chiffres : `data/gold/kpi.csv`. Validation humaine obligatoire avant diffusion.*

## Synthèse

Le marché allemand est attractif : la TECH y croît de 2,9 % par an [K1a] contre -1,3 % [K1a] en France, et les dépenses par habitant atteignent 363,0 € [K10_detail] contre 204,2 € [K10_detail]. Mais la rentabilité n'est pas acquise : avec des achats en France et le loyer IHK, le résultat annuel d'un magasin est de -4,1 M€ [K12_resultat] (estimation) et le projet n'est jamais rentable [K12] (estimation).

L'arbitrage porte sur les achats et le loyer. Avec des achats locaux et un loyer au niveau France, le retour sur investissement atteint 7,9 années [K12] (estimation). Le loyer maximal pour un résultat positif est de 32,7 €/m²/mois [K12_seuil_loyer] (estimation). La marge brute TECH post-taxe n'est que de 12,2 % [K5] (estimation), face à Ceconomy, dont la part de marché est estimée entre 17,3 % [K3_bas] et 37,5 % [K3_haut] (estimation).

Nous recommandons un Go sous conditions : un magasin pilote à Cologne, avec achats via une centrale allemande, loyer inférieur au seuil [K12_seuil_loyer] et assortiment TECH et jeux vidéo. La décision de déploiement sera prise après la période d'exploitation du pilote.

## Commentaires par axe

### Marché & Potentiel
Le secteur TECH allemand croît de 2,9 % par an [K1a], quand le secteur français recule de -1,3 % [K1a]. Fnac Darty détient 17,3 % [K2] (estimation) du marché en France.

### Prix & Marges
L'indice de prix TECH Allemagne/France est de 81,3 [K4_ttc] (base France = 100), d'où une marge brute post-taxe estimée à 12,2 % [K5] (estimation). Les livres atteignent 30,8 % [K5] (estimation), mais leur éligibilité à l'assortiment est très faible.

### Réseau & Implantation
La densité Ceconomy est de 4 magasins par million d'habitants [K6] en Nordrhein-Westfalen, contre 4,7 [K6] au niveau national. Le loyer annuel d'un magasin de 2 400 m² au loyer IHK s'élève à 3,3 M€ [K7_magasin] (hypothèse).

### Opérations & Logistique
La distance moyenne depuis le hub de Chilly-Mazarin est de 618,6 km [K8]. Les droits de douane sont de 0 % [K9_douane].

### Assortiment
Le catalogue France est éligible à 92,4 % [K11_detail] (simulé) en TECH et à 89,3 % [K11_detail] (simulé) en jeux vidéo, contre 10,1 % [K11_detail] (simulé) en livres. Cela justifie un assortiment centré TECH et jeux vidéo.

### Synthèse
Un magasin de 2 400 m² génère un CA estimé à 14,6 M€ [K12_ca] (estimation) pour un investissement de 3,6 M€ [K12_invest] (hypothèse). Seul le scénario D (achats locaux, loyer niveau France) est rentable, avec un retour en 7,9 années [K12] (estimation).

## Risques

- **Loyer :** avec achats locaux et loyer IHK, le résultat reste de -2,4 M€ [K12_resultat] (estimation) et le projet est jamais rentable [K12] (estimation). Le loyer IHK repose sur une hypothèse [K7_magasin].
- **Sensibilité du retour :** si le CA baisse de 20 % et l'investissement atteint 2000 €/m², le retour passe à 13,2 années [K12_sensibilite] (estimation).
- **Concurrence :** Ceconomy pourrait détenir jusqu'à 37,5 % [K3_haut] (estimation) du marché TECH, avec une pression nationale estimée à 22,2 points de vente par million d'habitants [K6_national] (estimation).
