import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as intgr
import scipy.signal as sig

### Clarinette 

# Hypothèse : Zray = 0

# Constantes physiques
rho_air = 1.225
Cv = 1256
Cp = 7/5*Cv

## Pour la corde (de sol)
mu_s = 0.4
mu_d = 0.2
M1 = 6.42e-3  # masse modale
rho = 3.1e-3
T = 51.9
Z = np.sqrt(T * rho)
c0_cordes = np.sqrt(T / rho)

w = .015 #Largeur de l'anche
H = .002 #espace antre l'anche et le bec


### Récupérer les coeffs modaux

def coeffs_modaux_bois(c0, l, rc, damping=False,ray=False):
    
    f = np.linspace(20,10000,5000)
    om = 2*np.pi*f
    k = om/c0
    pi = np.pi
    k = 2 * pi * f / c0
    #Z_c = rho_air * c0 / S_cylinder
    Z_c = 1  # car adimensionné ? 
    
    if damping:
        gamma = 1j * k + (1 + 1j) * 3e-5 * np.sqrt(f) / rc
        A = np.cosh(gamma * l)
        B = Z_c * np.sinh(gamma * l)
        C = 1 / Z_c * np.sinh(gamma * l)
        D = np.cosh(gamma * l)
    else:
        A = np.cos(k * l)
        B = 1j * Z_c * np.sin(k * l)
        C = 1j / Z_c * np.sin(k * l)
        D = np.cos(k * l)
        
    if ray :
        Z_L = np.square(k*rc)/4 + 1j*0.6*k*rc
        p_end = 1
        U_end = p_end/Z_L
        p_0,U_0 = A*p_end+B*U_end, C*p_end+D*U_end
        Ze = p_0/U_0
    else :
        Ze = B/D
        
    peaks,_ = sig.find_peaks(np.abs(Ze))

    Ym = 1/np.abs(Ze)[peaks]
    fr_m = f[peaks]
    
    Fm = 2*c0/l
    
    return Fm, Ym, fr_m

def coeffs_modaux_cordes(c0,l,beta):
    
    f = np.linspace(20,20000,10000)
    om = 2*np.pi*f
    k = om/c0
    
    
    Zm = -1j*Z*(np.tan(k*beta*l)**(-1) + np.tan(k*(1-beta)*l)**(-1))
    Y = 1/Zm
    peaks,_ = sig.find_peaks(abs(Y))
    
    Ym = abs(Y)[peaks]
    fr_m = f[peaks]
    
    Fm = 1/M1
    
    return Fm, Ym, fr_m
    

### Fonctions caractéristiques

def coeffs_F(gamma, zeta):
    """Calcule les coefficients de la fonction de
    couplage F linéarisée
    F(p) = F0 + Ap + Bp**2 + Cp**3
    """
    if gamma == 0:
        return 0, 0, 0, 0
    else:
        F0 = zeta * (1 - gamma) * np.sqrt(gamma)
        A = zeta * (3 * gamma - 1) / 2 / np.sqrt(gamma)
        B = -zeta * (3 * gamma + 1) / 8 / gamma ** (3 / 2)
        C = -zeta * (gamma + 1) / 16 / gamma ** (5 / 2)
    return F0, A, B, C

def Fclarinette(list_p, gamma, zeta):
    """
    Renvoit le débit u suivant la pression p
    suivant la relation u = F(p)
    """
    if gamma == 0:
        return np.zeros(len(list_p))
    else:
        valid = (gamma - list_p < 1) & (gamma - list_p > 0)
        sgn = (gamma - list_p) / np.abs(gamma - list_p)
        # u = zeta * (1 - gamma + list_p) * np.nan_to_num(np.sqrt(gamma - list_p)) * valid
        u = zeta * (1 - gamma + list_p) * np.sqrt(np.abs(gamma - list_p)) * valid * sgn
    return u

def Fcordes(v,n,gamma,zeta):
    dv = gamma - v
    alpha = np.sqrt(mu_s*(mu_s-mu_d))
    eps = 1e-4
    return zeta*(mu_d*dv*np.sqrt(dv**2 + eps/(n**2))+2*alpha*dv/n)/(dv**2 + 1/(n**2))

### Dérivées des fonctions caractéristiques

#def deriveeBois(p,pprim,gamma,zeta):
#    if gamma == 0:
#        return np.zeros(len(p))
#    else:
#        valid = (gamma - p < 1) & (gamma - p > 0)
#        derivee = valid * (zeta * np.nan_to_num(np.sqrt(gamma-p)) + zeta*(1-gamma+p)*(-1/2/np.nan_to_num(np.sqrt(gamma-p))))
#    return pprim*derivee

def deriveeCordes(v,vprim,gamma,zeta):
    alpha = np.sqrt(mu_s*(mu_s-mu_d))
    eps = 1e-4
    dv = gamma - v
    n = 25
    denom = (dv**2 +1/n**2)**2
    racine = np.sqrt(dv**2 + eps/(n**2))
    return -vprim*zeta*((1/n**2)*(2*alpha/n + mu_d*(racine + (dv**2)/racine))+mu_d*(dv**4)/racine - mu_d*(dv**2)*racine - 2*alpha*(dv**2)/n)/denom


########### SIMULATIONS

def clarinette(
    t_max,
    sample_rate,
    nb_modes,
    gamma,
    zeta,
    l,
    c0,
    rc = 0.02,
    rampe=False,
    fig=False,
    sound=False,
):
    Fm, Ym, fr_m = coeffs_modaux_bois(c0=c0,rc=rc,l=l)
    #fr_m = (2*np.arange(0,len(Ym))+1)*c0/l/4
    omega = 2*np.pi*fr_m

    Nsim = int(t_max*sample_rate)
    tps = np.linspace(0,Nsim/sample_rate,Nsim)
    
    F0, A, B, C = coeffs_F(gamma, zeta)

    def deriv_nbmodes(t,X):
        derivF = np.sum(X[1::2])*(A + 2*B*np.sum(X[0::2]) + 3*C*np.sum(X[0::2])**2)
        Xprim = np.zeros(nb_modes*2)                                       
        Xprim[1::2] = Fm*derivF - Ym[0:nb_modes]*X[1::2] - np.square(omega[0:nb_modes])*X[0::2]  
        Xprim[0::2] = X[1::2]
        return Xprim
    
    X0 = np.zeros(2*nb_modes)
    X0[0::2] = 0.01/nb_modes
    
    sol = intgr.solve_ivp(fun = deriv_nbmodes, t_span = (0,t_max), y0 = X0, t_eval = tps, dense_output= False, method = 'RK45')
    #print(sol['message'])

    p = np.sum(sol['y'][0::2],axis=0)
    
    u = Fclarinette(p,gamma,zeta)
    
    if fig :
        plt.figure(figsize = (15,3))
        plt.plot(sol['t'],p)
        plt.xlim(0,0.5)
        plt.show()
        
    return p, u, tps

def cordes(
    t_max,
    sample_rate,
    nb_modes,
    gamma,
    zeta,
    beta,
    l,
    rampe=False,
    fig=False,
    sound=False,
):
    
    n = 25
    
    Fm, Ym, fr_m = coeffs_modaux_cordes(c0=c0_cordes,l=l,beta=beta)
    #print(Fm)
    #print(fr_m)
    #print(c0_cordes)
    omega = 2*np.pi*fr_m

    Nsim = int(t_max*sample_rate)
    tps = np.linspace(0,Nsim/sample_rate,Nsim)
    
    def deriv_nbmodes(t,X):
        Xprim = np.zeros(nb_modes*2) 
        Xprim[0::2] = X[1::2]
        
        derivF = deriveeCordes(v=np.sum(X[0::2]),vprim=np.sum(X[1::2]),gamma=gamma,zeta=zeta)
        Xprim[1::2] = - Ym[0:nb_modes]*X[1::2] - np.square(omega[0:nb_modes])*X[0::2] + Fm*derivF
        return Xprim
    
    X0 = np.zeros(2*nb_modes)
    X0[0::2] = gamma/nb_modes
    
    sol = intgr.solve_ivp(fun = deriv_nbmodes, t_span = (0,t_max), y0 = X0, t_eval = tps, dense_output= False, method = 'RK45')
    #print(sol['message'])

    v = np.sum(sol['y'][0::2],axis=0)
    
    f = Fcordes(v,n,gamma,zeta)
    
    if fig :
        plt.figure(figsize = (15,3))
        plt.plot(sol['t'],v)
        plt.xlim(0,0.5)
        plt.show()
        
    return v, f, tps
    
### Fonction générale de simulation
    
def modal(
    instrument,
    t_max,
    sample_rate,
    nb_modes,
    gamma,
    zeta,
    l,
    c0=340,
    beta=0.3,
    rampe=False,
    fig=False,
    sound=False,
):
    if instrument == "clarinette":
        return clarinette(
            t_max,
            sample_rate,
            nb_modes,
            gamma,
            zeta,
            l,
            c0,
            rc = 0.02,
            rampe=rampe,
            fig=fig,
            sound=sound,
        )

    if instrument == "corde":
        return cordes(
            t_max,
            sample_rate,
            nb_modes,
            gamma,
            zeta,
            beta,
            l,
            rampe=rampe,
            fig=fig,
            sound=sound,
        )
    else:
        print("Mauvais nom d'instrument : 'clarinette' ou 'corde' ")
        return 0
    
#t_max = 1
#sample_rate = 22050

#p,_,tps = clarinette(t_max=t_max,sample_rate=sample_rate,nb_modes=1,gamma=0.5,zeta=0.4,l=60e-2,c0=340)