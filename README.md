[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Auto-oscillations
Projet de recherche dans le cadre du M2 ATIAM

## Résumé 

La synthèse sonore par modèles physiques permet de produire une grande variété de sons riches, très différents de ceux obtenus avec d’autres méthodes de synthèse (additive, par modulation…). Les progrès de l’électronique et de l’informatique ont permis d’utiliser cette méthode en temps réel. Les instruments auto-oscillants -instruments à vents et cordes frottées - sont particulièrement intéressants car ils présentent plusieurs régimes de fonctionnement. L’approche par modèles physiques possède également l’avantage de produire une connaissance physique des instruments considérés et de permettre le contrôle de paramètres ayant une signification physique. Le contrôle des instruments auto-oscillants - et par conséquent des modèles associés - pour produire des sons musicaux est un exercice délicat. Il est donc nécessaire d’identifier les bons paramètres qui permettent d’obtenir le son désiré. Nous proposons ici une implémentation de quelques modèles physiques d'instruments auto-oscillants pour réaliser des simulations et construire des cartographies des régimes d'oscillations explorés par les instruments en fonction des paramètres physiques régissant leurs comportements. Ces modèles permettent d'obtenir une meilleure intuition musicale du comportement des instruments et de réaliser une implémentation temps réel de leur synthèse avec une interface utilisateur adaptée utilisant les cartographies permettant d'assister le contrôle.

## Plan 

1. Modélisation physique des instruments de musique auto-oscillants (clarinette, cordes frottées, saxophone et cuivres) par méthode de guide d'onde et décomposition modale.
2. Cartographie des régimes de fonctionnement de ces instruments par apprentissage automatique (SVM).
3. Implémentation temps réel du modèle modal pour la clarinette sous MaxMSP / Gen, implémentation du solveur Runge-Kutta d'ordre 4.

### Exemples audios 

Site web : https://pliplouf.github.io/Auto-oscillations/

## Notice
<pre>
modelisation_physique :   
  bifurcations.py : Trace un diagramme de bifurcation.   
      Ligne 17 : Entrer les paramètres relatifs au calcul.   
      Ligne 32 : Entrer un modèle (modal par défaut) et les paramètres supplémentaires si besoin.   
  Modele_modal_fct_rampe.py : Donne un son simulé de clarinette, violon ou saxophone.   
      A la fin du code il faut commenter/décommenter l'instrument que l'on souhaite modéliser (par défaut c'est la clarinette qui est décommentée).   
      Ligne 434 : tmax correspond à la durée de simulation.   
      gamma_velo correspond tantôt à gamma pour la clarinette et le sax, tantôt à la vitesse dans le cas du violon.   
      zeta_force : même logique pour zeta et la force.   
      durete_rampe : correspond à la vitesse de l'attaque entre 20 et 2000.   
      l_resonateur : longueur du résonateur.   
  resonateur.py : Calcule la fonction de transfert de la caisse d'un violon sur la base d'un vecteur p correspondant à la vitesse au chevalet.   
  McIntyre-violon.py : Simule un son de violon, avec la possibilité de changer la fonction F (modélisant la non-linéarité du contact archet-corde).
  McIntyre_anche.py : Simule un son d'instrument à anche, avec un modèle simplifié de dynamique d'anche. L'anche est décrite par les paramètres Q et omega qui sont respectivement le facteur de qualité et la fréquence de résonance de l'anche.
</pre>
