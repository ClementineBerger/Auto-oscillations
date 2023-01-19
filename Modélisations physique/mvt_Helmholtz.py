import numpy as np
import matplotlib.pyplot as plt 

### Définition des paramètres

def retardT(L,c):
    '''Renvoie T le retard accumulé par l'onde
    en un aller-retour
    L : longueur du guide cylindrique
    c : célérité des ondes dans l'air
    '''
    return 2*L/c

### Définition des fonctions

def coeffs(gamma,zeta):
    '''Calcule les coefficients de la fonction de
    couplage F linéarisée
    F(p) = F0 + Ap + Bp**2 + Cp**3
    '''
    F0 = zeta*(1-gamma)*np.sqrt(gamma)
    A = zeta*(3 * gamma - 1) / 2 /np.sqrt(gamma)
    B = -zeta*(3*gamma+1)/8/gamma**(3/2)
    C = -zeta*(gamma+1)/16/gamma**(5/2)
    return F0,A,B,C

def Fapprox(p,F0,A,B,C,gamma,zeta):
    '''Renvoit le débit u suivant la pression p
    suivant la relation u = F(p) selon la version
    linéarisée de la fonction'''
    if gamma - p >= 1 or gamma - p < 0:  # anche battante
        return 0
    else:
        return F0 + A * p + B * p**2 + C * p**3

def rotationGapprox(x,F0,A,B,C,gamma,zeta):
    '''Calcule G = la fonction F rotatée de 45° :
    pour un point (p,u), renvoit les coordonnées dans l'espace (p-, p+)
    suivant la version linéarisée de la fonction F
    '''
    theta = np.pi/4
    rotation_matrix = np.array([[np.cos(theta), -np.sin(theta)],[np.sin(theta), np.cos(theta)]])
    y = Fapprox(x,F0,A,B,C,gamma,zeta)
    X = rotation_matrix @ np.array([[x],[y]])
    return X


def Gapprox(x, F0, A, B, C, liste_G, x_G):
    '''Calcule la fonction y=G(x) suivant la version
    linéarisée de F'''
    ind = 0
    while x_G[ind] < x:
        ind += 1
    return liste_G[ind]


def GCalApprox(x, F0, A, B, C, eps, Z0):
    '''Calcule la fonction y=G(x) avec ajout d'une
    faible impédance de rayonnement eps*Z0'''
    X = Gapprox(x, F0, A, B, C)
    return X * (Z0 - eps) / (Z0 + eps)


def F(p, gamma, zeta):
    '''Renvoit le débit u suivant la pression p
    suivant la relation u = F(p)'''
    if gamma - p >= 1 or gamma - p < 0:
        return 0
    else:
        return zeta * (1 - gamma + p) * np.sqrt(gamma - p)


def rotation_G(x, gamma, zeta):
    '''Calcule G = la fonction F rotatée de 45° :
    pour un point (p,u), renvoit les coordonnées dans l'espace (p-, p+)
    '''
    theta = np.pi / 4
    rotation_matrix = np.array(
        [[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]]
    )
    y = F(x, gamma, zeta)
    X = rotation_matrix @ np.array([[x], [y]])
    return X


def G(p, gamma, zeta, liste_G, x_G):
    '''Calcule la fonction y=G(x) suivant la version
    linéarisée de F'''
    ind = 0
    while x_G[ind] <= p:
        ind+=1
    return liste_G[ind]

def definition_listes_G(gamma, zeta,borne_min, borne_max, nb_pts,approx=False):
    '''Définition des listes (x,y) définissant la fonction y=G(x)
    
    gamma : contrôle de la pression de bouche
    zeta : contrôle anche
    borne_min, borne_max : couple des bornes de x
    nb_pts : nombre de points de calcul
    '''
    x = np.linspace(-borne_min, borne_max, nb_pts)
    liste_G = np.zeros_like(x)
    x_G = np.zeros_like(x)
    if approx :
        for i in range(len(x)):
            X = rotationGapprox(x[i], gamma, zeta)
        liste_G[i] = X[1]
        x_G[i] = X[0]
    else :
        for i in range(len(x)):
            X = rotation_G(x[i], gamma, zeta)
            liste_G[i] = X[1]
            x_G[i] = X[0]
    
    return x_G, liste_G

def simulation(t_max, fe, gamma, zeta, L, c,approx=False, fig=False):
    '''Renvoit la pression p et le débit u (adimensionnés) simulés avec
    les paramètres gamma, zeta :
    
    t_max : durée de la simulation en s
    fe : fréquence d'échantillonnage de la simulation en Hz
    gamma : contrôle de la pression de bouche
    zeta : contrôle anche
    L : longueur du cylindre
    c : célérité des ondes
    '''
    
    
    # Initialisation des paramètres
    T = retardT(L,c)
    
    compute_time = np.arange(int(t_max / T)) * T  # temps de calcul de l'amplitude
    sim_time = (np.arange(int(t_max * fe)) / fe)  # temps de "remplissage" pour avoir un signal carré
    
    Ncompute = len(compute_time)
    Nsim = len(sim_time)

    # Initialisation des listes de calcul des pressions adimensionnée p+ et p-
    # au temps de calcul
    Pmoins_compute = np.zeros(Ncompute)
    Pplus_compute = np.zeros(Ncompute)
    
    F0,A,B,C = coeffs(gamma,zeta)
    
    # Définition de la fonction G
    x_G, liste_G = definition_listes_G(gamma, zeta, -3, 3, 2500,approx=approx)
    
    ########### Simulation
    
    # Initialisation 
    p0 = F0/(1-A)
    u0 = F(p0,gamma,zeta)

    Pmoins_compute[0] = (p0 - u0) / 2
    Pplus_compute[0] = (p0 + u0) / 2
    
    # Calculs

    if approx :
        for i in range(1, Ncompute):
            Pmoins_compute[i] = -Gapprox(Pmoins_compute[i - 1], F0, A, B, C, liste_G, x_G)
            X = Gapprox(Pmoins_compute[i], F0, A, B, C, liste_G, x_G)
            Pplus_compute[i] = X
    else :
        for i in range(1, Ncompute):
            Pmoins_compute[i] = -G(Pmoins_compute[i - 1], gamma, zeta, liste_G, x_G)
            X = G(Pmoins_compute[i], gamma, zeta, liste_G, x_G)
            Pplus_compute[i] = X
        
    # Remplissage pour un signal créneau

    Pmoins = np.zeros(Nsim)
    Pplus = np.zeros(Nsim)
        
    i = 0
    ind = 0
    while i < Nsim and ind < Ncompute:
        Pmoins[i] = Pmoins_compute[ind]
        Pplus[i] = Pplus_compute[ind]
        i += 1
        time = i / fe
        ind = int(time // T)

    p = Pmoins + Pplus
    u = Pmoins - Pplus
    
    # Plot figure
    
    if fig :
        plt.figure(figsize=(7,7),dpi=150)
        plt.plot(compute_time,Pmoins_compute,color='k',label=r'$p^-$')
        plt.plot(compute_time,Pplus_compute,color='k',label=r'$p^+$')
        plt.plot(sim_time,p,color='grey',label=r"pression $p$")
        plt.xlabel('Temps en s',size=14)
        plt.ylabel(r'pression $p$',size=14)
        plt.legend(fontsize=14)
        plt.grid()
        plt.xlim(0, 0.3)
        plt.tight_layout()
        
    return p, u
    
    