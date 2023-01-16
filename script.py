# p(t) = (r*(p+Zu))(t) + Zu(t)
# u(t) = F(p(t))

# (r*p)(t) = sum p(t-t') r(t') dt

import numpy as np

# Ici on suppose que F est donnée sous la forme d'un tableau
# F : tableau des F(p_i) pour p_i allant de p_0 à p_end
# p_m : pression dans la bouche
# r_dt : caractérise l'onde réfléchie
# attention, on doit avoir sum(r_dt) = -1

def embouchure(p_m, F, Z, r_dt, p_0=0, p_end=1):
    nt = len(p_m)
    pression = np.copy(p_m)
    flux = np.zeros(nt)
    
    n_F = len(F)
    p_F = np.linspace(p_0,p_end,n_F)
    test = p_F - Z*F
    print(test)
    for t in range(nt):
        t2 = min(t,len(r_dt)-1)
        q = np.sum(pression[t-t2:t]*r_dt[t2:0:-1])
        print(q)
        # résoudre p = q + Z F(p)
        i = np.argmin(np.abs(test-q))
        pression[t] += p_F[i]
        flux[t] = F[i]
    return pression,flux

# OK le code marche, mais pour l'instant ça fait tout le temps zéro parce qu'il faut commencer à souffler dans l'instrument quelque part quand même n'est-ce pas
p_m = 0.4*np.ones(30)
F = np.sin(np.linspace(0,1)*np.pi)
r_dt = np.array([0,0,-1])
