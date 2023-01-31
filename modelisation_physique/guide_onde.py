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
# type_reflection = dirac ou triangle (essayer de rajouter gaussien)
# frac_T = pour le type triangle -> défini la demi largeur du triangle égale à T/frac_T



### Définition des fonctions 

def retardT(L,c):
    '''
    Renvoie T le retard accumulé par l'onde
    en un aller-retour
    L : longueur du guide cylindrique
    c : célérité des ondes dans l'air
    '''
    return 2*L/c

def coeffs(gamma,zeta):
    '''Calcule les coefficients de la fonction de
    couplage F linéarisée
    F(p) = F0 + Ap + Bp**2 + Cp**3
    '''
    if gamma == 0:
        return 0, 0, 0, 0
    else :
        F0 = zeta*(1-gamma)*np.sqrt(gamma)
        A = zeta*(3 * gamma - 1) / 2 /np.sqrt(gamma)
        B = -zeta*(3*gamma+1)/8/gamma**(3/2)
        C = -zeta*(gamma+1)/16/gamma**(5/2)
    return F0,A,B,C

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

def convolution(ind_tau,reflex_list,signal_list):
    '''
    Calcul de la convolution entre le signal p + u et la fonction de réflexion 
    (aux temps passés) avec une intégration par la méthode des trapèzes
    
    ind_tau = indice du temps de calcul
    reflex_list = liste des coefficients de réflexion dans le temps
    signal_list = liste p + u 
    
    (plus rapide que scipy...)
    '''
    
    x1 = reflex_list[0:ind_tau+1]
    x2 = np.flipud(signal_list[0:ind_tau+1])
    
    integrate = intgr.trapz(y=x1*x2)  
    #integrate = intgr.trapz(reflex_list*np.flipud(signal_list))
    
    return integrate

def convolution_triangle(ind_tau,T,fe,frac_T,reflex_list,signal_list):
    '''
    Calcul de la convolution entre le signal p + u et la fonction de réflexion 
    (aux temps passés) avec une intégration par la méthode des trapèzes
    
    ind_tau = indice du temps de calcul
    reflex_list = liste des coefficients de réflexion dans le temps
    signal_list = liste p + u 
    
    (plus rapide que scipy...)
    '''
    
    indT = int(T*fe)
    
    delta_ind = indT//frac_T
    
    if ind_tau <= indT - delta_ind :
        return 0
    
    elif ind_tau <= indT +delta_ind :
        x1 = reflex_list[indT-delta_ind:ind_tau+1]
        x2 = np.flipud(signal_list[0:ind_tau-(indT-delta_ind)+1])
    
    else : 
        x1 = reflex_list[indT-delta_ind:indT+delta_ind+1]
        x2 = np.flipud(signal_list[ind_tau-(indT+delta_ind):ind_tau-(indT-delta_ind)+1])
    
    integrate = intgr.trapz(y=x1*x2)  
    
    return integrate

def reflexion(T,frac_T,rate_gauss,fe,Nsim,type):
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
        
    elif type == 'gauss':
        demi_largeur = rate_gauss*T
        sigma = demi_largeur/np.sqrt(2*np.log(2))
        b = 1/(2*(sigma**2))
        a = 1/(sigma*np.sqrt(2*np.pi))    ### à revoir, le fait que l'aire de r doit être égale à 1
        tps = np.linspace(0,Nsim/fe,Nsim)
        reflex_list = -np.exp(-b*((tps-T)**2))
        reflex_list /= -np.sum(reflex_list)
                    
    return reflex_list

def simulation(t_max, fe, gamma, zeta, type_reflection, L, c, frac_T=10, rate_gauss = 0.4,fig=False, sound=False):
    '''
    Renvoit la pression p et le débit u (adimensionnés) simulés avec
    les paramètres gamma, zeta :
    
    t_max : durée de la simulation en s
    fe : fréquence d'échantillonnage de la simulation en Hz
    gamma : contrôle de la pression de bouche
    zeta : contrôle anche
    type_reflection : type de réflexion au bout du guide, 'dirac', 'triangle' ou 'gauss'
    frac_T : seulement pour le type 'triangle', définition de la demi-largeur du triangle T/frac_T
    rate_gauss : demi-largeur à mi-hauteur (typiquement entre 0.05 et 0.4)
    L : longueur du cylindre
    c : célérité des ondes
    '''
    
    # Initialisation des paramètres
    T = retardT(L,c)
    indT = int(T*fe)
    
    #F0, A, B, C = coeffs(gamma, zeta)
    
    time = (np.arange(int(t_max * fe)) / fe)  # temps de simulation
    Nsim = len(time)
    
    p = np.zeros(Nsim)
    u = np.zeros(Nsim)
    
    reflex_list = reflexion(T,frac_T,rate_gauss,fe,Nsim,type=type_reflection)
    
    ######## SIMULATION
    
    tab_p, tab_F = tableau_F(-5,5,2000,gamma,zeta)
    solvF = tab_p - tab_F

    i_act = np.argmin(np.abs(tab_p-gamma)) + 1
    
    if type_reflection=='dirac':
        for j in range(Nsim): 
            if j < indT :
                ph = -(p[0]+u[0])
            else :
                ph = -(p[j-indT]+u[j-indT])
            i = find_zero(solvF-ph,i_act)
            i_act = i
            p[j] = tab_p[i]
            u[j] = tab_F[i]
            #disc = (A-1)**2 -4*B*(F0+ph)
            #p_fixe = (1-A-np.sqrt(disc))/(2*B)
            #p_fixe = (ph+F0)/(1-A)
            #p[j] = p_fixe
            #u[j] = F(np.array([p_fixe]),gamma,zeta)
    
    elif type_reflection=='triangle':
        for j in range(Nsim): 
            ph = convolution_triangle(ind_tau=j,T=T,fe=fe,frac_T=frac_T,reflex_list = reflex_list, signal_list = p + u)
            i = find_zero(solvF-ph,i_act)
            i_act = i
            p[j] = tab_p[i]
            u[j] = tab_F[i]
            #p_fixe = (ph+F0)/(1-A)
            #p[j] = p_fixe
            #u[j] = F(np.array([p_fixe]),gamma,zeta)
            
    elif type_reflection=="gauss":
        for j in range(Nsim): 
            ph = convolution(ind_tau=j,reflex_list = reflex_list, signal_list = p + u)
            i = find_zero(solvF-ph,i_act)
            i_act = i
            p[j] = tab_p[i]
            u[j] = tab_F[i]
            #p_fixe = (ph+F0)/(1-A)
            #p[j] = p_fixe
            #u[j] = F(np.array([p_fixe]),gamma,zeta)
        
    if fig :
        plt.figure(figsize=(10,5))
        plt.plot(time,p)
        plt.xlim(0,0.2)
        plt.ylim(-1.1, 1.1)
        plt.tight_layout()
        plt.xlabel("Temps en s",size=14)
        plt.ylabel("Amplitude",size=14)
        plt.show()
        
    #if sound :
    #    display(Audio(p,rate=fe))
        
    return p, u