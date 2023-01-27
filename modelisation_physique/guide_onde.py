"""

@author : Clémentine BERGER & Amélie PICARD

Implémentation guide d'onde suivant l'article de McIntyre : à l'avantage d'être plus modulable
avec la possibilité de changer de fonction de réflexion au bout du guide d'onde

"""


### Importation des bibliothèques

import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as sig
import scipy.integrate as intgr
from IPython.display import Audio

### Paramètres utilisateurs 

# c = célérité des ondes sonores
# L = longueur du guide d'onde
# gamma = rapport pression de bouche / pression de plaquage
# zeta = paramètre caractéristique de l'anche


### Définition des fonctions 

def retardT(L,c):
    '''
    Renvoie T le retard accumulé par l'onde
    en un aller-retour
    L : longueur du guide cylindrique
    c : célérité des ondes dans l'air
    '''
    return 2*L/c

def F(list_p, gamma, zeta):
    '''
    Renvoit le débit u suivant la pression p
    suivant la relation u = F(p)
    '''
    if gamma == 0:
        return np.zeros(len(list_p))
    else :
        valid = (gamma - list_p < 1) & (gamma - list_p > 0)
        u = zeta * (1 - gamma + list_p) * np.nan_to_num(np.sqrt(gamma - list_p)) * valid
    return u
    
def tableau_F(pmin,pmax,nb_pts,gamma,zeta):
    '''
    Rempli un tableau F pour faire la recherche de 0 
    
    pmin = borne inférieure de p
    pmax = borne supérieure de p
    nb_pts = nombre de points de calculs
    gamma = 
    zeta =
    
    '''
    tab_p = np.linspace(pmin,pmax,nb_pts)
    tab_F = F(tab_p, gamma, zeta)
    
    return tab_p, tab_F

def find_zero(tableau, i):
    """
    Recherche le point d'annulation de tableau le plus proche possible de i
    
    tableau = tableau des valeurs de la fonction F sur l'intervalle souhaité
    i =  
    """
    l = len(tableau)
    changement_signe = tableau[0:l-1]*tableau[1:l] # il y a un point d'annulation entre tableau[j] et tableau[j+1] ssi tableau[j]*tableau[j+1] <= 0
    negatif = changement_signe <= 0 # True aux indices où il y a un changement de signe
    tab_i0 = (np.arange(l-1))[negatif] # indices auxquels il y a un changement de signe
    if len(tab_i0)==0:
        return np.argmin(np.abs(tableau))
    i0 = np.argmin(np.abs(tab_i0-i)) # indice de l'indice le plus proche de i dans tab_i0
    return tab_i0[i0]

def convolution(ind_tau,reflex_list,signal_list,time):
    '''
    Calcul de la convolution entre le signal p + u et la fonction de réflexion 
    (aux temps passés) avec une intégration par la méthode des trapèzes
    
    ind_tau = indice du temps de calcul
    reflex_list = liste des coefficients de réflexion dans le temps
    signal_list = liste p + u 
    '''
    
    x1 = reflex_list[0:ind_tau+1]
    x2 = np.flipud(signal_list[0:ind_tau+1])
    
    integrate = intgr.trapz(y=x1*x2)  
    
    return integrate

def reflexion(T,frac_T,fe,Nsim,type):
    '''
    Calcule la liste des coefficients de réflexion pour plusieurs formes de fonction de réflexion
    
    type = str donnant le type de réflexion choisi ; 'dirac', 'triangle' 
    (si possible 'exponentiel' mais nécessite de revoir un peu le code...)
        - dirac : r(t) = -delta(t-T)
        - triangle : triangle négatif centré en T (plus il est court, plus on se rapproche du dirac et des créneaux)
    '''
    
    indT = int(T*fe)   #indice du moment T de la réflexion au bout du guide
    
    reflex_list = np.zeros(Nsim)
    
    if type == 'dirac' :
        reflex_list[indT] = -1
    
    elif type == 'triangle' : #centré en T
        delta_ind = indT//frac_T
        pente = 1/delta_ind

        for i in range(indT-delta_ind, indT+1):
            reflex_list[i] = (i-indT+delta_ind)*pente

        for i in range(indT+1, indT+delta_ind+1):
            reflex_list[i] = reflex_list[indT] - (i-indT)*pente
            
        aire = np.sum(reflex_list)

        reflex_list = -reflex_list/aire 
        
    return reflex_list

def simulation(t_max, fe, gamma, zeta, type_reflection, L, c, frac_T=10 ,fig=False, sound=False):
    '''
    Renvoit la pression p et le débit u (adimensionnés) simulés avec
    les paramètres gamma, zeta :
    
    t_max : durée de la simulation en s
    fe : fréquence d'échantillonnage de la simulation en Hz
    gamma : contrôle de la pression de bouche
    zeta : contrôle anche
    type_reflection : type de réflexion au bout du guide, 'dirac' ou 'triangle'
    frac_T : seulement pour le type 'triangle', définition de la demi-largeur du triangle T/frac_T
    L : longueur du cylindre
    c : célérité des ondes
    '''
    
    # Initialisation des paramètres
    T = retardT(L,c)
    
    time = (np.arange(int(t_max * fe)) / fe)  # temps de simulation
    Nsim = len(time)
    
    p = np.zeros(Nsim)
    u = np.zeros(Nsim)
    
    reflex_list = reflexion(T,frac_T,fe,Nsim,type=type_reflection)
    
    ######## SIMULATION
    
    tab_p, tab_F = tableau_F(-5,5,2000,gamma,zeta)
    solvF = tab_p - tab_F

    i_act = np.argmin(np.abs(tab_p-gamma)) + 1
    
    for j in range(Nsim): 
        
        ph = convolution(ind_tau=j,reflex_list = reflex_list, signal_list = p + u,time=time)
        i = find_zero(solvF-ph,i_act)
        i_act = i
        p[j] = tab_p[i]
        u[j] = tab_F[i]
        
    if fig :
        plt.figure(figsize=(10,5))
        plt.plot(time,p,label="McIntyre")
        #plt.plot(sim_time,p_maganza*np.max(p)/np.max(p_maganza),label="Maganza")
        plt.xlim(0,0.2)
        plt.ylim(-1.1, 1.1)
        plt.tight_layout()
        plt.xlabel("Temps en s",size=14)
        plt.ylabel("Amplitude",size=14)
        plt.legend(fontsize=14)
        plt.show()
        
    #if sound :
    #    display(Audio(p,rate=fe))
        
    return p, u