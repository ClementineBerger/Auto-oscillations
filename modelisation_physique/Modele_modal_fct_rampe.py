# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 11:10:51 2023

@author: Romain Caron
"""
import numpy as np
import matplotlib.pyplot as plt
import platform
import time as tim
import soundfile as sf
import os
import sounddevice as sd
import tempfile


#---------------------------------------Méthodes de Runge-Kutta 

def RK4(X, tmax, nb_mode, sample_rate, args, vecs, vio):                    #Ordre 4

    """
        Inputs : the initial state variable X and other parameters
        
        Do : differential equation resolution Runge-Kutta order 4
        
        Returns : the pressure signal
        
    """
    
    (Fbis,omegabis,Y_mbis,pair,impair,x_out) = vecs     # Récupération des variables compactées
    (As, Bs, Cs) = args                                 
    
    dt = 1/sample_rate                                  # Time step for Runge-Kutta method
    x2 = np.zeros(int(sample_rate*tmax))                # Initialization of the output signal x2
    x2[0]=sum(impair*X)                                 # The first step is directly extracted from the state variable 
    
    for i in range(int(sample_rate*tmax-1)):        # Time loop 
        args2 = (As[i], Bs[i], Cs[i], vio)                # Update of the parameters for the 
        k1 = func(X, nb_mode, args2, vecs)                # First RK coefficient
        
        k1x = [x*dt/2 for x in k1]                        # Interpolation of the coef
        k2 = func(np.add(X, k1x), nb_mode, args2, vecs)   # Second RK coefficient
        
        k2x = [x*dt/2 for x in k2]                        # Same of the other coefs
        k3 = func(np.add(X, k2x), nb_mode, args2, vecs)
        
        k3x = [x*dt for x in k3]                          # This time the time step is dt and not dt/2
        k4 = func(np.add(X, k3x), nb_mode, args2, vecs)
        
        k2s = [x*2 for x in k2]                           # Application of the coefs in the final formula
        k3s = [x*2 for x in k3]

        Xs = np.add(np.add(np.add(k1, k2s), k3s), k4)     # Final sum of RK4
        Xsx = [x*dt/6 for x in Xs]                        # dt/6 coefficient
        X = np.add(X, Xsx)                                # Addition to the initial X

        x2[i+1] = sum(impair*X)                           # Put the sum of X in the output signal
    return x2

#---------------------------------------- Définition du système \Dot{X}=f(X)

def func_anche_simple(x, nb_mode, args, vecs):

    """
        Inputs : the initial state variable x and other parameters
        
        Returns : x_out : the derivative of x for the single reed
        
    """
    
    (A, B, C, vio) = args                                            # Picking the compacted parameters
    (Fbis,omegabis, Y_mbis, pair, impair, x_out) = vecs
    
    commun = sum(x*pair)*(A + 2*B*sum(x*impair) + 3*C*sum(x*impair)**2)        # Derivative of the F(p) function
    
    x_out = np.zeros(nb_mode*2)                                                # Initialization of the output vector
    x_out[1:] = Fbis[1:]*commun - (Y_mbis*x)[1:] - (np.power(omegabis, 2)*x)[:-1]    # Computing the \Dot{p} values
    x_out[:-1] = x_out[:-1] + (x*pair)[1:]                                           # Computing the p values

    return x_out

def func_violon(x, nb_mode, args, vecs):
    
    """
        Inputs : the initial state variable x and other parameters
        
        Returns : x_out : the derivative of x for the rubbed string
        
    """
    
    (A, B, C, vio) = args                                           # Picking the compacted parameters
    (zeta_force, sigma, coef_frott_dyn_corde)  = vio
    (Fbis, omegabis, Y_mbis, pair, impair, x_out) = vecs
    
    xpair = sum(x*pair)             # Pre-computing the sums of modal speed
    ximpair = sum(x*impair)         # Pre-computing the sums of modal speed derivative
    
    commun = zeta_force*np.exp(-sigma*ximpair**2)*xpair\
                       *(np.sqrt(sigma)*(2.33164 - 0.00186532*sigma)*ximpair**2 
                         + 0.0127324*coef_frott_dyn_corde
                                    *np.exp(sigma*ximpair**2)
                         + 0.000932658*np.sqrt(sigma) 
                         - (4.66329 + 5)*sigma**(3/2)*ximpair**4
                         )\
                       /(ximpair**2 + 0.0004)                         # Derivative of the F(p) function

    x_out = np.zeros(nb_mode*2)                                     # Initialization of the output vector
    x_out[1:] = Fbis[1:]*commun - (Y_mbis*x)[1:] - (np.power(omegabis, 2)*x)[:-1]    # Computing the \Dot{v} values
    x_out[:-1] = x_out[:-1] + (x*pair)[1:]                                       # Computing the v values

    return x_out

#------------------------------------------ Fonction pour jouer le son et enregistrer le wav
def play(y, Fe=44100):
    rep=1
    z=np.real(y)/(abs(np.real(y)).max())
    if platform.system()=='Darwin': #MAC (sous linux sounddevice a un comportement erratique)
        sd.play(z,Fe)
        return
    fichier=tempfile.mktemp()+'SON_TP.wav'
    sec=len(y)/Fe
    if sec<=20:
        rep=True
    if sec>20:
        print ('Vous allez créer un fichier son de plus de 20 secondes.')
        rep=None
        while rep is None:
            x=input('Voulez-vous continuer? (o/n)')
            if x=='o':
                rep=True
            if x=='n':
                rep=False
            if rep is None:
                print ('Répondre par o ou n, merci. ')
    if rep:
        fichier2='son.wav' #Adresse du fichier exporté, à modifier
        sf.write(fichier,z,Fe)
        sf.write(fichier2,z,Fe)     #Ecrit le fichier wav dans le fichier
        os.system(''+fichier+' &')
        
#------------------------------------------------ Fonction faisant tourner le modèle

def simulation(gamma_velo, zeta_force, tmax, sample_rate, l_resonateur, nb_mode, instrument, durete_rampe,c0=340,
                beta=0.3,
                type_reflection="dirac",
                rampe=False,
                t_rampe=0.2,
                pertes_dirac=1,
                frac_T=10,
                rate_gauss=0.1,
                fig=False,
                sound=False,
            ):
                    

    #----------------------------------------- Definitions
    nb_mode = int(nb_mode)
    plt.close(1)    
    c0 = 340;               # Sound speed
    vio = 0;                # Initialization of pack variable vio
    time = np.linspace(0,tmax,int(sample_rate*tmax))     # Time vector
    As = Bs = Cs = np.zeros(len(time)); # Initialization of pack variables
    global func         # Make the name func global so that it will be recognized by the other functions
    
    
    #----------------------------------------- Rampe
    
    # Faire varier durete_rampe entre 20 (pente douce) et 2000 (pente raide)
    if rampe:
        gammas = np.arctan(np.linspace(0.1, durete_rampe, len(time)))\
                *gamma_velo/(np.arctan(durete_rampe)) # Définition de gamma_velo au cours du temps de la simulation
    else:
        gammas = gamma_velo*np.ones(len(time))
    
    #----------------------------------------- Instrument choice
    
    if instrument == 'clarinette':
        #--------------------------------------------------------------------Clarinette
        rayon_pavillon = 0;
        #------------------------------------------Sélection de fonction
        func = func_anche_simple;
        
        #------------------------------------------Admittances
        #Y_m = np.ones(nb_mode)*1 /1233.36096998528                    #Initialisation de toutes les admittances à une valeur par défaut
        Y_m = np.ones(nb_mode)*1 /5233.36096998528
        #------------------------------------------Fréquences
        freq = np.zeros(nb_mode)                                    #Initialisation générale fréquences des modes
        #l_effectif = l_resonateur                                    #Cas Clarinette Zs=0
        l_effectif = l_resonateur + (8*rayon_pavillon/(3*np.pi))      #Cas Clarinette bafflée
        #l_effectif = l_resonateur + 0.6*rayon_pavillon               #Cas Clarinette non bafflée
        freq = (2*np.arange(nb_mode) + 1)*c0/(4*l_effectif)         #Cas particulier de la clarinette (quintoie)
        omega = freq*2*np.pi                                        #Conversion freq/puls
        As = zeta_force*(3*gammas - 1) /2 /np.sqrt(gammas)          #Paramètres pour l'équation du modèle
        Bs = -zeta_force*(3*gammas+1)/8/gammas**(3/2)
        Cs = -zeta_force*(gammas +1)/16/gammas**(5/2)
        
    elif instrument == 'saxophone':
        #--------------------------------------------------------------------Saxophone
        rayon_pavillon = 6e-2
        #------------------------------------------Sélection de fonction
        func = func_anche_simple;
        
        #------------------------------------------Admittances
        Y_m = np.ones(nb_mode)*1 /1233.36096998528                  #Initialisation de toutes les admittances à une valeur par défaut
        #------------------------------------------Fréquences
        freq = np.zeros(nb_mode)                                    #Initialisation générale fréquences des modes
        #l_effectif = l_resonateur                                    #Cas Zs=0
        l_effectif = l_resonateur + (8*rayon_pavillon/(3*np.pi))      #Cas bafflé
        #l_effectif = l_resonateur + 0.6*rayon_pavillon               #Cas non bafflé
        freq = np.arange(1, nb_mode + 1)*c0/(2*l_effectif)          #Cas particulier du Sax (octavie)
        omega = freq*2*np.pi                                        #Conversion freq/puls
        As = zeta_force*(3*gammas - 1) /2 /np.sqrt(gammas)          #Paramètres pour l'équation du modèle
        Bs = -zeta_force*(3*gammas+1) /8 /gammas**(3/2)
        Cs = -zeta_force*(gammas + 1) /16 /gammas**(5/2)
        
    elif instrument == 'violon':
    
        #--------------------------------------------------------------------Violin
        #----------------------------------------- Parameters
        diametre_corde = 1.35e-3;
        
        tension_corde = 51.9*1.14;
        sigma = 1.8;
        position_archet = 10e-2;
        #position_archet = 3e-2;
        mass_vol_corde = 3.1e-3 / (np.pi*(0.8e-3 /2)**2);
        young_corde = 5e9;
        moment_quad_corde = 2.01e-14;
        #coef_frott_dyn_corde = 0.2;
        coef_frott_dyn_corde = 0.35;
        #Les valeurs numériques sont extraites de la thèse de Vigué
        
        
        #------------------------------------------Sélection de fonction
        func = func_violon;
        
        
        #------------------------------------------Fréquences
        freq = np.zeros(nb_mode)                                      #Initialisation générale fréquences des modes

        freq = (np.arange(1, nb_mode + 1)*np.pi)/(2*l_resonateur)\
               *np.sqrt(tension_corde/(mass_vol_corde*(np.pi*(diametre_corde/2)**2)))\
               *np.sqrt(1 + ((young_corde*moment_quad_corde/(2*tension_corde))
                           *(np.arange(1, nb_mode + 1)**2*np.pi**2
                             /(l_resonateur**2)))) 
               
        omega = freq*2*np.pi                  #Conversion freq/puls
        
        
        #------------------------------------------Admittances
        Yc = (tension_corde*mass_vol_corde*np.pi*(diametre_corde/2)**2)**(-1/2) # Characteristic admittance string
        
        Y_m = 1j*Yc*(np.tan(omega/c0*position_archet)**(-1)
                   + np.tan(omega/c0*(l_resonateur-position_archet))**(-1))**(-1)
        
        vio = (zeta_force, sigma, coef_frott_dyn_corde)             # Storage of violin's variables in vio
        
        
    else:       # Error raising if name didn't match 
        raise ValueError("Veuillez indiquer un nom d'instrument correct : clarinette,saxophone")
    

    #----------------------------------------- Computed variables   
                     
    coeff_modaux = 2*c0/l_resonateur*np.ones(nb_mode)     #Modal coefficients
    
    args = (As, Bs, Cs)       #Packing in args
    
    
    #----------------------------------------- Usefull vectors for computing
    
    pair = np.arange(nb_mode*2) %2        #Vecteur à multiplier avec X pour avoir les dérivées uniquement
    impair = (np.arange(nb_mode*2) + 1) %2    #Vecteur à multiplier avec X pour avoir les non-dérivées uniquement
    x_out = np.zeros(nb_mode*2)                               
    Fbis = np.zeros(nb_mode*2)              #Conversion de F pour qu'il fasse la taille nb_mode*2
    Fbis[1::2] = coeff_modaux
    omegabis = np.zeros(nb_mode*2)
    omegabis[::2] = omega
    Y_mbis = np.zeros(nb_mode*2)
    Y_mbis[1::2] = abs(Y_m)
    vecs=(Fbis, omegabis, Y_mbis, pair, impair, x_out)          #Packing in vecs
    
    
    #----------------------------------------- Lancement
    
    #t1 = tim.time()                   #Démarrage du timer
    X = 0.01*impair                  #Initialisation de X avec p_n = gamma_velo à l'instant 0

    p = RK4(X, tmax, nb_mode, sample_rate, args, vecs, vio)                   #Appel de la résolution
    #tcalc = tim.time() - t1             #Arrêt du timer
    #print("Temps de calcul : "+str(tcalc)+"s")
    
    if sound == True:
        play(p)                         #Ecoute du son
        
    
    if fig == True:
        #-----------------------------------------------Plots
        plt.figure(1)
        plt.plot(time, p, 'orange', linewidth = 2)
        plt.xlabel('time (s)')
        plt.ylabel('pressure')
        plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
        plt.xlim()
        plt.grid(True)


    return p,time


if __name__ == "__main__":

    #------------------------------------------------ Lancement du modèle
    
    #------------- Clarinette
    
    p, time = simulation(tmax = 2,
                         nb_mode = 5,
                         instrument = 'clarinette', 
                         sample_rate = 44100, 
                         gamma_velo = 0.6, 
                         zeta_force = 0.8, 
                         durete_rampe = 2000, 
                         l_resonateur = 60e-2, 
                         fig = True, sound = True
                         )
    
    
    #------------- Saxophone
    """
    p, time = simulation(tmax = 2, 
                         nb_mode = 5, 
                         instrument = 'saxophone', 
                         sample_rate = 44100, 
                         gamma_velo = 0.7, 
                         zeta_force = 0.8, 
                         durete_rampe = 2000, 
                         l_resonateur = 1.335, 
                         fig = True, sound = True
                         )
    """
    #------------- Violon
    """
    p, time = simulation(tmax = 2, 
                         nb_mode = 5, 
                         instrument = 'violon', 
                         sample_rate = 44100, 
                         gamma_velo = 0.2, 
                         zeta_force = 0.0105, 
                         durete_rampe = 2000, 
                         l_resonateur = 0.33, 
                         fig = True, sound = True
                         )
    """