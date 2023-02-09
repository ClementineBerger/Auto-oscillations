# p(t) = (r*(p+Zu))(t) + Zu(t)
# u(t) = F(p(t))

# Pour le violon : p devient v, f devient F

# (r*p)(t) = sum p(t-t') r(t') dt

"""
Différentes fonctions F d'après Clémentine :
F(v) = F_max/mu_s (mu_d + (mu_s-mu_d) Phi(v-v_bow)) avec Phi = ??
F(v) = F_max/mu_s (v-v0)/v0 (1+(v-v0)²/v0²)^{-1}

"""

import numpy as np
import matplotlib.pyplot as plt

"""
sample_rate = 44100
F0 = 440 # fréquence supposée de l'instrument, en Hz
t_max = .2 # durée de la simulation, en s

T = 1/F0 # période supposée de l'instrument, en s
T1 = T//1.8 # aller-retour de l'onde en passant par le chevalet
T2 = T-T1 # aller-retour de l'onde en passant par l'autre bout

i_T1 = int(sample_rate*T1)
i_T2 = int(sample_rate*T2)
r_dt = np.zeros(i_T1+i_T2)
r_dt[i_T1]=.8
r_dt[-1]=1
r_dt = -0.95*r_dt/np.sum(r_dt)
"""

"""
Fonction de réflexion d'après Clémentine :
r(t) = Y/2*(1 + h1(t) + h2(t) + h1*h2(t) + h2*h1(t) + h1*h2*h1(t) + ...)
mais vu que moi je prends des Dirac et qu'ils ne se superposent pas, les produits de convolution sont nuls et on a simplement
r(t) = Y/2(1+h1+h2)
"""

nt = int(t_max*sample_rate)
n_F = 201

tableau_des_temps = np.linspace(0, t_max, nt)




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

def F_violon(n_F, n_adh, v_bow):
    # Cette sous-fonction renvoie un tableau gamma_F allant de -1 à 1, et un tableau flux_F = F(gamma_F)
    # gamma_m est la pression dans la bouche (ou équivalent)
    n_moins = (n_F-n_adh)*(1+v_bow)/2
    n_moins = int(n_moins)
    n_plus = n_F-n_adh-n_moins
    v_moins = np.linspace(-1,v_bow,n_moins)
    v_zero = np.ones(n_adh)*v_bow
    v_plus = np.linspace(v_bow,1,n_plus)
    v_F = np.concatenate((v_moins,v_zero,v_plus))
    force_moins = np.exp(v_moins-v_bow)
    force_zero = np.linspace(1,-1,n_adh)
    force_plus = -np.exp(v_bow-v_plus)
    force_F = np.concatenate((force_moins, force_zero, force_plus))
    return v_F, force_F


def corde(v_bow, r_dt, nt, zeta0=0.5):
    
    v_t = np.zeros(nt) # les tableaux en _t sont ceux qui donnent le résultat, en fonction du temps
    force_t = np.zeros(nt)
    
    v_F, force_F = F_violon(200, 50, v_bow)
        
    i_act = np.argmin(np.abs(v_F-v_bow))
    T2 = len(r_dt)-1
    
    for t in range(nt):
        if t<T2:
            q = np.sum((v_t[0:t]+force_t[0:t])*r_dt[t:0:-1])
        else:
            q = np.sum((v_t[t-T2:t]+force_t[t-T2:t])*r_dt[T2:0:-1])
        # v + a.v' = v + a(v-v[t-1])/dt = v(1+a/dt) - v[t-1].a/dt
        i = resoudre(v_F - zeta0*force_F - q, i_act) # p + ap' - Zf = q
        v_t[t] = v_F[i]
        force_t[t] = zeta0*force_F[i]
        
    return v_t,force_t

"""
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
"""


def simulation(
    t_max,
    sample_rate,
    gamma,
    zeta,
    l,
    c0,
    beta = 2/5,
    pertes = 1,
    fig = False,
    sound = False
):
    
    F0 = c0/2/l # fréquence supposée de l'instrument, en Hz
    T = 1/F0 # période supposée de l'instrument, en s
    T1 = T*beta # aller-retour de l'onde en passant par le chevalet
    i_T1 = int(sample_rate*T1)
    i_T = int(sample_rate*T)
    
    r_dt = np.zeros(i_T)
    r_dt[i_T1]=-pertes/2
    r_dt[-1]=-1/2

    vitesse_t,_ = corde(gamma,r_dt,nt,zeta)
    if fig:
        plt.plot(tableau_des_temps,vitesse_t)
        plt.xlabel("temps (s)")
        plt.ylabel("vitesse (corde//violon)")
        plt.title("Simulation violon")
        plt.show()
    return vitesse_t


"""
for v in range(10):
    vitesse,_ = embouchure(v/10, 0.95*r_dt, nt)
    plt.plot(tableau_des_temps+v/F0/20,v/10-vitesse,label="v_bow = "+str(v/10))
plt.legend()
plt.xlabel("temps")
plt.ylabel("vitesse corde")

plt.show()

ampl = []
vit = []
for m in range(400):
    p_m = m/400
    vit.append(p_m)
    pression,_ = embouchure(p_m, r_dt, nt)
    ampl.append(amplitude(pression))
plt.plot(vit,ampl)
plt.xlabel("vitesse de l'archet")
plt.ylabel("amplitude résultante")
plt.title("bifurcation")
plt.show()

"""
