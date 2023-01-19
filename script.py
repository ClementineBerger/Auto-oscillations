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
ANCHE SANS MASSE ET SANS RIGIDITÉ
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
    

def embouchure(p_m, Z, r_dt, nt, p_0=-1, p_end=1):
    pression = np.zeros(nt)
    flux = np.zeros(nt)
    
    n_F = 200
    p_F = np.linspace(p_0,p_end,n_F)
    F = (p_m-p_F)*(p_F-p_end)
    test = p_F - Z*F
    
    i_act = np.argmin(np.abs(p_F-p_m))
    
    T2 = len(r_dt)-1
    
    for t in range(nt):
        if t<T2:
            q = np.sum((pression[0:t]+Z*flux[0:t])*r_dt[t:0:-1])
        else:
            q = np.sum((pression[t-T2:t]+Z*flux[t-T2:t])*r_dt[T2:0:-1])
        # résoudre p = q + Z F(p)
        try:
            i = resoudre(test-q, i_act)
        except:
            print("t = ", t)
            print("pression = ", p_F[i_act])
            plt.plot(p_F,test)
            plt.plot(p_F,q*np.ones(n_F))
            plt.show()
        i_act = i
        pression[t] = p_F[i]
        flux[t] = F[i]
    return pression,flux


def amplitude(pression):
    nt = len(pression)
    MAX = np.max(pression[nt//2:])
    MIN = np.min(pression[nt//2:])
    return MAX-MIN

import matplotlib.pyplot as plt

r_dt = np.array([0,0,-0.9])
nt = 50

pression,_ = embouchure(0, .5, r_dt, nt)
plt.plot(range(nt),pression,label="p_m=0")
pression,_ = embouchure(0.2, .5, r_dt, nt)
plt.plot(range(nt),pression,label="p_m=0.2")
pression,_ = embouchure(0.4, .5, r_dt, nt)
plt.plot(range(nt),pression,label="p_m=0.4")
pression,_ = embouchure(0.6, .5, r_dt, nt)
plt.plot(range(nt),pression,label="p_m=0.6")
plt.legend()
plt.xlabel("temps")
plt.ylabel("pression")
plt.show()

# Pourquoi ça commence à -1 ?

ampl = []
pres = []
for m in range(400):
    p_m = m/1000
    pres.append(p_m)
    pression,_ = embouchure(p_m, .5, r_dt, nt)
    ampl.append(amplitude(pression))
plt.plot(pres,ampl)
plt.xlabel("pression dans la bouche")
plt.ylabel("amplitude pression résultante")
plt.title("bifurcation")
plt.show()

# OK donc le régime permanent est bien atteint à nt/2, c'est pas à cause de ça

# Z n'a absolument aucune importance
"""
Qui c'est qui fait des calculs sur le script python parce que flemme de sortir du papier ? C'est moi

p(t) = (r*(p+Zu))(t) + ZF(p(t))
p(t)-ZF(p(t)) = -p(t-T)-ZF(p(t-T))
Supposons que T est une anti-période, alors dp(t-T)=-dp(t) :
2p0 - ZF(p0+dp(t)) + ZF(p0-dp(t)) = 0
ou sinon sans le DL :
ZF(p) = sin(pi p)
sin(p0-dp) - sin(p0+dp) = cos(p0)sin(dp)
donc p0 = cos(p0) sin(dp) sauf que du coup on a des arcsin(truc plus grand que 1)
"""
