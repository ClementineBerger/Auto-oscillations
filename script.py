# p(t) = (r*(p+Zu))(t) + Zu(t)
# u(t) = F(p(t))
"""
Hypothèses du modèle :
la pression se décompose sous forme de pression aller + pression retour
et le flux se décompose sous forme de flux aller - flux retour
-> linéarité du résonateur (ça c'est courant)

Autre hypothèse : à l'intérieur de l'embouchure, u = F(p) et p = +- Zu
avec Z indépendant de omega
-> pas d'équation différentielle, pas de dynamique
ANCHE SANS MASSE
"""
# (r*p)(t) = sum p(t-t') r(t') dt

import numpy as np

# Ici on suppose que F est donnée sous la forme d'un tableau
# F : tableau des F(p_i) pour p_i allant de p_0 à p_end
# p_m : pression dans la bouche
# r_dt : caractérise l'onde réfléchie
# attention, on doit avoir sum(r_dt) = -1

def resoudre(tableau, i):
    # recherche le point d'annulation de tableau le plus proche possible de i
    l = len(tableau)
    changement_signe = tableau[0:l-1]*tableau[1:l] # il y a un point d'annulation entre tableau[j] et tableau[j+1] ssi tableau[j]*tableau[j+1] <= 0
    negatif = changement_signe <= 0 # True aux indices où il y a un changement de signe
    tab_i0 = (np.arange(l-1))[negatif] # indices auxquels il y a un changement de signe
    if len(tab_i0)==0:
        return np.argmin(np.abs(tableau))
    i0 = np.argmin(np.abs(tab_i0-i)) # indice de l'indice le plus proche de i dans tab_i0
    return tab_i0[i0]
    

def embouchure(p_m, Z, r_dt, nt=1, zeta=0.5):
    # ce qui est noté p c'est gamma, c'est la pression entre -1 et 1
    if type(p_m)==int or type(p_m)==float:
        P_m = np.ones(nt)*p_m
    else:
        P_m = p_m
        p_m = P_m[0]
        nt = len(P_m)
    
    pression = np.zeros(nt)
    flux = np.zeros(nt)
    
    n_F = 201
    p = np.linspace(-1,1,n_F)
    F = np.zeros(n_F)
    imin = int(p_m*n_F/2)
    imax = int((p_m+1)*n_F/2)
    F[imin:imax] = zeta * (1 - p_m + p[imin:imax]) * np.sqrt(p_m - p[imin:imax])
    test = p - Z*F
    
    i_act = np.argmin(np.abs(p-p_m))
    
    T2 = len(r_dt)-1
    
    for t in range(nt):
        
        if P_m[t] != p_m:
            p_m = P_m[t]
            imin = int(p_m*n_F/2)
            imax = int((p_m+1)*n_F/2)
            F[imin:imax] = zeta * (1 - p_m + p[imin:imax]) * np.sqrt(p_m - p[imin:imax])
            F[:imin] = 0
            F[imax:] = 0
            test = p - Z*F
    
        if t<T2:
            q = np.sum((pression[0:t]+Z*flux[0:t])*r_dt[t:0:-1])
        else:
            q = np.sum((pression[t-T2:t]+Z*flux[t-T2:t])*r_dt[T2:0:-1])
        # résoudre p = q + Z F(p)
        # C'est cette équation qui suppose l'anche sans masse
        if t < 2 :
            terme_inertiel = 0
        else:
            terme_inertiel = m_dt2*(p+pression[t-2]-2*pression[t-1])
        i = resoudre(test+terme_inertiel-q, i_act) # p + mp'' - Zf = q
        i_act = i
        pression[t] = p[i]
        flux[t] = F[i]
    return pression,flux


def amplitude(pression):
    nt = len(pression)
    MAX = np.max(pression[nt//2:])
    MIN = np.min(pression[nt//2:])
    return MAX-MIN

import matplotlib.pyplot as plt

r_dt = np.array([0]*20+[1])
r_dt = -1*r_dt/np.sum(r_dt)
nt = 500
n_att = 30

p = 6

for m_dt2 in [0,1,10,100,1000]:
    P_m = p/10*np.ones(nt)
    P_m[:n_att] = np.linspace(0,p/10,n_att)
    #P_m = P_m + np.random.random(nt)*0.1
    pression,_ = embouchure(0.6, 1, 0.95*r_dt, nt)
    plt.plot(range(nt),pression,label=str(m_dt2))
plt.xlabel("temps")
plt.ylabel("pression")
plt.title("Différentes inerties")
plt.legend()
plt.show()
"""
ampl = []
pres = []
for m in range(400):
    p_m = m/400
    pres.append(p_m)
    pression,_ = embouchure(p_m, 1, r_dt, nt)
    ampl.append(amplitude(pression))
plt.plot(pres,ampl)
plt.xlabel("pression dans la bouche")
plt.ylabel("amplitude pression résultante")
plt.title("bifurcation")
plt.show()

"""
"""
Anche parfaite : f = F(p)

Of course the finite mass of a real clarinet reed, the inertia in the unsteady air flow through the gap, and the fact that the pressure p in the player's mouth cannot really be constant,
all introduce departures from the assumed behavior especially at high frequencies
"""
