# p(t) = (r*(p+Zf))(t) + Zf(t)
# f(t) = F(p(t))
# xi'' + alpha xi' + omega² xi = A p_m + B p

# En changeant simplement la masse de l'anche, on passe d'une anche simple à un cuivre

import numpy as np
import matplotlib.pyplot as plt

sample_rate = 44100

def resoudre(tableau, i):
    # recherche le point d'annulation de tableau le plus proche possible de i
    l = len(tableau)
    changement_signe = tableau[0:l-1]*tableau[1:l] # il y a un point d'annulation entre tableau[j] et tableau[j+1] ssi tableau[j]*tableau[j+1] <= 0
    negatif = changement_signe <= 0 # True aux indices où il y a un changement de signe
    tab_i0 = (np.arange(l-1))[negatif] # indices auxquels il y a un changement de signe
    if len(tab_i0)==0:
        return np.argmin(np.abs(tableau))
    i0 = np.argmin(np.abs(tab_i0-i)) # indice de l'indice le plus proche de i dans tab_i0
    index = tab_i0[i0]
    if abs(tableau[index])<abs(tableau[index+1]):
        return index
    return index+1
    

def embouchure(gamma_m, r_dt, nt, omega = 4224/sample_rate, zeta0=0.5):
    
    gamma_t = np.zeros(nt) # les tableaux en _t sont ceux qui donnent le résultat, en fonction du temps
    flux_t = np.zeros(nt)
    
    n_F = 201
    gamma_F = np.linspace(-1,1,n_F) # les tableaux en _F sont ceux qui servent à calculer la fonction non-linéaire F
    flux_F = np.zeros(n_F)          # flux_F = F(pression_F)
    imin = int(gamma_m*n_F/2)
    imax = int((gamma_m+1)*n_F/2)
    flux_F[imin:imax] = (1 - gamma_m + gamma_F[imin:imax]) * np.sqrt(gamma_m - gamma_F[imin:imax])
    # Attention : à chaque usage de flux_F dans le futur, il faudra multiplier par z !!
    
    #omega = 4224/sample_rate
    z = 0
    z_past = 0
    
    i_act = np.argmin(np.abs(gamma_F))
    
    T2 = len(r_dt)-1
    
    for t in range(nt):
        if t<T2:
            q = np.sum((gamma_t[0:t]+flux_t[0:t])*r_dt[t:0:-1])
        else:
            q = np.sum((gamma_t[t-T2:t]+flux_t[t-T2:t])*r_dt[T2:0:-1])
        # résoudre p = q + Z F(p)
        i = resoudre(gamma_F -zeta0*(z+1)*flux_F -q, i_act)
        i_act = i
        gamma_t[t] = gamma_F[i]
        flux_t[t] = zeta0*(z+1)*flux_F[i]

         # z'' = omega²(p_m - p) - omega z' - omega² z
        # Euler explicite
        """
        z2 = A*p_m+B*p[i]-alpha*z1-omega2*z
        z = z+z1
        z1 = z1+z2
        """
        # Euler implicite ?
        # z'' = (z_futur + z_past - 2z)/4dt²
        # z' = (z_futur - z_past)/2dt
        # donc (1/2dt + alpha) z_futur = 2dt(A p_m + B p - omega² z) + alpha z_past + (2z-z_past)/2dt
        z_futur = 2/sample_rate*(omega**2*(gamma_m - gamma_F[i]) - omega**2*z) + omega*z_past + (2*z-z_past)/2*sample_rate
        z_futur = z_futur/(omega+1/2*sample_rate)
        z_past = z
        z = max(z_futur,0)
        z = min(z_futur,1)
        
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

F = 110 # fréquence supposée de l'instrument, en Hz
t_max = 0.5 # durée de la simulation, en s

T = int(sample_rate/F) # période supposée de l'instrument, en Hz
r_dt = np.array([0]*T+[1])
#r_dt = np.exp(-(np.linspace(0,40,20)-20)**2/20)r_dt[0]=0
r_dt = -0.95*r_dt/np.sum(r_dt)
nt = int(t_max*sample_rate)
n_att = 30

for p in range(10):
    pression,_ = embouchure(p/10, r_dt, nt)
    plt.plot(range(nt),pression, label=str(p/10))
plt.legend()
plt.xlabel("temps")
plt.ylabel("pression")
plt.savefig("anche.pdf", transparent=True,bbox_inches = "tight")


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
