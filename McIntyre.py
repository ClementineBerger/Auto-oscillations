# p(t) = (r*(p+Zu))(t) + Zu(t)
# u(t) = F(p(t))

# (r*p)(t) = sum p(t-t') r(t') dt

import numpy as np

# Ici on suppose que F est donnée sous la forme d'un tableau
# F : tableau des F(p_i) pour p_i allant de p_0 à p_end
# p_m : pression dans la bouche
# r_dt : caractérise l'onde réfléchie
# attention, on doit avoir sum(r_dt) = -1

# NOTE : PASSER DE L'IMPÉDANCE À LA RÉFLEXION ET VICE-VERSA
# impédance ramenée pour pouvoir comparer les deux modèles

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

def F(n_F, gamma_m):
    # Cette sous-fonction renvoie un tableau gamma_F allant de -1 à 1, et un tableau flux_F = F(gamma_F)
    # gamma_m est la pression dans la bouche (ou équivalent)
    gamma_F = np.linspace(-1,1,n_F) # les tableaux en _F sont ceux qui servent à calculer la fonction non-linéaire F
    flux_F = np.zeros(n_F)          # flux_F = F(pression_F)
    imin = int(gamma_m*n_F/2)
    imax = int((gamma_m+1)*n_F/2)
    flux_F[imin:imax] = (1 - gamma_m + gamma_F[imin:imax]) * np.sqrt(gamma_m - gamma_F[imin:imax])
    return gamma_F, flux_F


def embouchure(gamma_m, r_dt, nt, zeta0=0.5):
    
    gamma_t = np.zeros(nt) # les tableaux en _t sont ceux qui donnent le résultat, en fonction du temps
    flux_t = np.zeros(nt)
    
    gamma_F, flux_F = F(201, gamma_m)
        
    i_act = np.argmin(np.abs(gamma_F-gamma_m))
    
    T2 = len(r_dt)-1
    
    for t in range(nt):
        if t<T2:
            q = np.sum((gamma_t[0:t]+flux_t[0:t])*r_dt[t:0:-1])
        else:
            q = np.sum((gamma_t[t-T2:t]+flux_t[t-T2:t])*r_dt[T2:0:-1])
        
        if t < 2 :
            terme_inertiel = 0
        else:
            terme_inertiel = m_dt2*(gamma_F+gamma_t[t-2]-2*gamma_t[t-1])
        
        i = resoudre(gamma_F -zeta0*flux_F +terme_inertiel-q, i_act) # p + mp'' - Zf = q
        gamma_t[t] = gamma_F[i]
        flux_t[t] = zeta0*flux_F[i]
        
    return gamma_t,flux_t


def amplitude(pression):
    nt = len(pression)
    MAX = np.max(pression[nt//2:])
    MIN = np.min(pression[nt//2:])
    return MAX-MIN

def frequence(pression):
    if amplitude(pression)==0: return 0
    nt = len(pression)
    fourier = np.fft.fft(pression[nt//2:])
    return np.argmax(fourier[:nt//5])

import matplotlib.pyplot as plt

r_dt = np.array([0]*20+[1])
#r_dt = np.exp(-(np.linspace(0,40,20)-20)**2/20)
r_dt[0]=0
r_dt = -1*r_dt/np.sum(r_dt)
m_dt2 = 20
nt = 500
n_att = 30

for m_dt2 in [0]:#,0.1,0.5,1,2,5,8,10]:
    ampl = []
    freq = []
    for p in range(0,100):
        #P_m = p/10*np.ones(nt)
        #P_m[:n_att] = np.linspace(0,p/10,n_att)
        #P_m = P_m + np.random.random(nt)*0.1
        pression,_ = embouchure(p/100, 0.95*r_dt, nt)
        #ampl.append(amplitude(pression))
        #freq.append(frequence(pression))
        plt.plot(range(nt),pression,label="p_m ="+str(p/10))
    #plt.plot(range(100),moy,label="m = "+str(m_dt2))
plt.legend()
plt.xlabel("p_m")
plt.ylabel("moyenne")

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
