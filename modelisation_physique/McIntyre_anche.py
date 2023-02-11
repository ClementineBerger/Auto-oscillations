import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

sample_rate = 44100
F0 = 440 # fréquence supposée de l'instrument, en Hz
t_max = .1 # durée de la simulation, en s

T = 1/F0 # période supposée de l'instrument, en s
i_T = int(sample_rate*T) # période supposée de l'instrument, en nb échantillon
r_dt = np.array([0]*i_T+[1])
r_dt = -0.95*r_dt/np.sum(r_dt)

nt = int(t_max*sample_rate)
n_F = 201

tableau_des_temps = np.linspace(0, t_max, nt)

def resoudre(tableau, i):
    """
    # recherche le point d'annulation de tableau le plus proche possible de i
    """
    l = len(tableau)
    changement_signe = tableau[0:l-1]*tableau[1:l] # il y a un point d'annulation entre tableau[j] et tableau[j+1] ssi tableau[j]*tableau[j+1] <= 0
    negatif = changement_signe <= 0 # True aux indices où il y a un changement de signe
    tab_i0 = (np.arange(l-1))[negatif] # indices auxquels il y a un changement de signe
    if len(tab_i0)==0:
        return np.argmin(np.abs(tableau))
    i0 = np.argmin(np.abs(tab_i0-i)) # indice de l'indice le plus proche de i dans tab_i0
    return tab_i0[i0]

def Fclarinette(n_F, gamma_m):
    """
    # Cette sous-fonction renvoie un tableau gamma_F allant de -1 à 1, et un tableau flux_F = F(gamma_F)
    # gamma_m est la pression dans la bouche (ou équivalent)
    """
    gamma_F = np.linspace(-1,1,n_F)
    flux_F = np.zeros(n_F)
    imin = int(gamma_m*n_F/2)
    imax = int((gamma_m+1)*n_F/2)
    flux_F[imin:imax] = (1 - gamma_m + gamma_F[imin:imax]) * np.sqrt(gamma_m - gamma_F[imin:imax])
    return gamma_F, flux_F

def embouche(X,t, gamma_F,flux_F, gamma_t,flux_t, m,a):
    """
    Fonction auxiliaire, à donner en paramètre à ode
    Cette fonction calcule X' en fonction de X et t
    Mais aussi, par effet de bord, elle stocke gamma et flux dans les tableaux gamma_t et flux_t,
    afin que leurs valeurs puissent être réutilisées (réflexion, tout ça)
    """
    (p,p1) = X

    i_t = int(t*sample_rate)
    if i_t >= nt:
        return (p1,(-p-a*p1)/m)

    # calcul de q (produit de convolution)
    if i_t<i_T:
        q = np.sum((gamma_t[0:i_t] + flux_t[0:i_t]) * r_dt[i_t:0:-1])
    else:
        q = np.sum((gamma_t[i_t-i_T:i_t] + flux_t[i_t-i_T:i_t]) * r_dt[i_T:0:-1])
            

    # calcul de f (résolution, si ça n'a pas déjà été fait)
    if flux_t[i_t]==0:
        i_p = int((p+1)/2*(n_F-.9))
        try:
            f = flux_F[i_p]
        except:
            f = 0
        flux_t[i_t]=f
        gamma_t[i_t]=p
    else:
        f = flux_t[i_t]
    
    p2 = (q + f - p - a*p1)/m
    return (p1,p2)

def embouchure(gamma_m, zeta0, omega, Q):
    """
    La grosse fonction
    """
    gamma_t = np.zeros(nt+5)
    flux_t = np.zeros(nt+5)
    
    gamma_F, flux_F = Fclarinette(n_F, gamma_m)
    flux_F = zeta0*flux_F

    m = 1/omega**2
    a = Q/omega

    la_fonction = lambda X,t: embouche(X,t, gamma_F,flux_F, gamma_t,flux_t,m,a)

    solve = odeint(la_fonction, (0,0), tableau_des_temps)
    
    return gamma_t[:nt]

def amplitude(pression):
    nt = len(pression)
    MAX = np.max(pression[nt//2:])
    MIN = np.min(pression[nt//2:])
    return MAX-MIN

def frequence(pression):
    if amplitude(pression)==0: return 0
    nt = len(pression)
    fourier = np.fft.fft(pression[nt//2:])
    return np.argmax(fourier[1:nt//4])


def simulation(
    t_max,
    sample_rate,
    gamma,
    zeta,
    type_reflection,
    l,
    c0,
    pertes = 1,
    omega_anche = 4224,
    Q_anche = 1,
    fig = False,
    sound = False
):
    
    F0 = c0/2/l # fréquence supposée de l'instrument, en Hz
    T = 1/F0 # période supposée de l'instrument, en s
    i_T = int(sample_rate*T) # période supposée de l'instrument, en nb échantillon
    r_dt = np.array([0]*i_T+[1])
    r_dt = -pertes*r_dt/np.sum(r_dt)
    
    nt = int(t_max*sample_rate)
    n_F = 201
    
    tableau_des_temps = np.linspace(0, t_max, nt)

    gamma_t = embouchure(gamma,zeta,omega_anche,Q_anche)
    if fig:
        plt.plot(tableau_des_temps, gamma_t)
        plt.xlabel("temps (s)")
        plt.ylabel("pression")
        plt.title("Simulation instrument à anche dynamique")
        plt.show()
    return gamma_t


"""
plt.subplot(2,1,1)
for p in range(5):
    pres = embouchure(p/5, 4224, 1)
    plt.plot(tableau_des_temps, pres, label="p_m = "+str(p/5))
plt.legend()
plt.title("Clarinette")

plt.subplot(2,1,2)
for p in range(5):
    pres = embouchure(p/5, 4224, 10)
    plt.plot(tableau_des_temps, pres, label="p_m = "+str(p/5))
plt.legend()
plt.title("Cuivre")

plt.show()
"""
