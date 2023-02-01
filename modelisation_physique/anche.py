# p(t) = (r*(p+Zf))(t) + Zf(t)
# f(t) = F(p(t))
# xi'' + alpha xi' + omega² xi = A p_m + B p

import numpy as np

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
    

def embouchure(p_m, r_dt, nt, A, zeta0=0.5):
    # ce qui est noté p c'est gamma, c'est la pression entre -1 et 1
    
    pression = np.zeros(nt)
    flux = np.zeros(nt)
    
    n_F = 201
    p = np.linspace(-1,1,n_F)
    F = np.zeros(n_F)
    imin = int(p_m*n_F/2)
    imax = int((p_m+1)*n_F/2)

    F[imin:imax] = (1 - p_m + p[imin:imax]) * np.sqrt(p_m - p[imin:imax])
    alpha = 0.1
    omega2 = 0.01
    B = -A
    z = zeta0
    z1 = 0
    
    i_act = np.argmin(np.abs(p-p_m))
    
    T2 = len(r_dt)-1
    
    for t in range(nt):
        if t<T2:
            q = np.sum((pression[0:t]+flux[0:t])*r_dt[t:0:-1])
        else:
            q = np.sum((pression[t-T2:t]+flux[t-T2:t])*r_dt[T2:0:-1])
        # résoudre p = q + Z F(p)
        i = resoudre(p-z*F-q, i_act)
        i_act = i
        pression[t] = p[i]
        flux[t] = F[i]
        
        # Euler explicite pour l'instant
        z2 = A*p_m+B*p[i]-alpha*z1-omega2*z
        z = z+z1
        z1 = z1+z2
    return pression,flux


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

r_dt = np.array([0]*60+[1])
#r_dt = np.exp(-(np.linspace(0,40,20)-20)**2/20)r_dt[0]=0
r_dt = -0.95*r_dt/np.sum(r_dt)
m_dt2 = 20
nt = 1000
n_att = 30

for A in [0,0.5,1,2,4,7]:
    pression,_ = embouchure(0.45, 0.95*r_dt, nt, A)
    plt.plot(range(nt),pression,label="A ="+str(A))
plt.legend()
plt.xlabel("temps")
plt.ylabel("pression")
plt.legend()
#plt.savefig("masse20.pdf", transparent=True,bbox_inches = "tight")

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
