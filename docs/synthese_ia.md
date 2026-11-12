# Synthèse pour le Comex

*Générée par : Claude (sonnet) via claude -p, chiffres contrôlés. Source des chiffres : `data/gold/kpi.csv`. Validation humaine obligatoire avant diffusion.*

## Synthèse

L'Allemagne offre un marché plus profond : 363,0 € de dépenses TECH par habitant [K10_detail] contre 204,2 € en France [K10_detail], où le secteur recule (-1,3 % par an [K1a]). Mais avec des achats depuis la France, un magasin perd de l'argent : -4,1 M€ par an (estimation) [K12_resultat] au loyer IHK, et son retour sur investissement est « jamais » [K12].

L'arbitrage tient aux achats et au loyer. Seul le scénario D (achats locaux, loyer au niveau France) est positif : 0,5 M€ par an (estimation) [K12_resultat], avec un retour en 7,9 années (estimation) [K12]. Dans le cas le plus défavorable testé, ce retour atteint 13,2 années (estimation) [K12_sensibilite]. La concurrence reste dense : 4,0 magasins CECONOMY par million d'habitants en Nordrhein-Westfalen [K6].

Nous recommandons un Go conditionnel : un magasin pilote à Cologne, avec achats via une centrale allemande, un loyer inférieur à 32,7 €/m²/mois (estimation) [K12_seuil_loyer] et un assortiment TECH et jeux vidéo, éligibles à 92,4 % et 89,3 % (simulé) [K11_detail]. Le déploiement sera décidé après deux ans d'exploitation.

## Commentaires par axe

### Marché & Potentiel
Le secteur TECH croît de 2,9 % par an en Allemagne [K1a], alors qu'il recule de 1,3 % en France [K1a]. CECONOMY y détient entre 17,3 % [K3_bas] et 37,5 % [K3_haut] du marché (estimation).

### Prix & Marges
En TECH, l'indice de prix allemand hors taxes est de 82,0 (FR = 100) [K4_ht], pour une marge brute post-taxe de 12,2 % (estimation) [K5]. Les livres atteignent 30,8 % (estimation) [K5].

### Réseau & Implantation
Le loyer annuel d'un magasin au tarif IHK est de 3,3 M€ (hypothèse) [K7_magasin]. La densité concurrentielle est de 4,0 magasins par million d'habitants en Nordrhein-Westfalen [K6], contre 4,7 en Allemagne [K6].

### Opérations & Logistique
Le hub de Chilly-Mazarin est à 618,6 km en moyenne des villes allemandes de taille importante [K8], sans droits de douane (0 % [K9_douane]). L'écart de TVA en TECH est de -1,0 point [K9_tva].

### Assortiment
47,2 % du catalogue France est éligible en Allemagne (simulé) [K11], dont 92,4 % en TECH [K11_detail] et 89,3 % en jeux vidéo [K11_detail] (simulé). Les livres ne le sont qu'à 10,1 % (simulé) [K11_detail].

### Synthèse
Le magasin n'est rentable que dans le scénario D, avec un retour en 7,9 années (estimation) [K12]. La sensibilité testée va de 4,4 années [K12_sensibilite] à 13,2 années [K12_sensibilite] (estimation).

## Risques

- **Loyer :** au loyer IHK avec achats locaux, le résultat annuel reste de -2,4 M€ (estimation) [K12_resultat] ; le seuil de 32,7 €/m²/mois (estimation) [K12_seuil_loyer] est donc une condition impérative.
- **Achats et marge :** sans centrale allemande, les scénarios avec achats France ne sont jamais rentables [K12], et la marge brute TECH post-taxe n'est que de 12,2 % (estimation) [K5].
- **Rentabilité incertaine :** le retour sur investissement varie de 4,4 [K12_sensibilite] à 13,2 années [K12_sensibilite] (estimation) selon le chiffre d'affaires et l'investissement, face à une concurrence de 4,0 magasins par million d'habitants en Nordrhein-Westfalen [K6].
