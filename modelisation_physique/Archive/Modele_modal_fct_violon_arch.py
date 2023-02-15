# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 11:10:51 2023

@author: Romain Caron
"""
import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
import platform
import time as tim
import soundfile as sf
import os
import sounddevice as sd
import tempfile

#------------------------------------------------Contrôle

gamma = 0.6
zeta = 0.2
nb_mode=2           #Nombre de modes à modéliser
dur=3;              #Durée de l'enregistrement à produire en secondes 
fs = 44100          #Fréquence d'échantillonnage
#L = 60e-2           #longueur clarinette
c = 343             #Vitesse son
#rc = 3e-2           #rayon de la clarinette


vb=0.6; #Vitesse transversale de l'archet (de l'ordre de 0.8)
Fb=0.4; #Force normale à la corde appliquée par l'archet (de l'ordre de 0.4)
        #Au plus on augmente Fb au plus il y a de bruit
v0=0.8;             #Coefficient v0
#------------------------------Corde

#dc=0.8e-3;           #Diamètre corde
dc=1.2e-3;
#Ec=500e6;            #Module d'Young corde
Ec=5e9 #D'après Vigué
#rhoc=2700;          #Masse volumique corde
rhoc=3.1e-3/(np.pi*(0.8e-3/2)**2);
L=0.33;          #Longueur corde violon
#L=0.6;
Lb=3e-2;           #Distance chevalet-archet
mud=0.2 #Coefficient de friction dynamique
#Tc=27*9.81/4;          #Tension de la corde (27kg pour 4 cordes)
#Tc=27*9.81/12.5; #G3
Tc=51.9/L
sigma=1.8;
Yc=(Tc*rhoc*np.pi*(dc/2)**2)**(-1/2)

#Ic=np.pi*dc**4/64;    #Moment quadratique corde
Ic=2.01e-14;
#------------------------------------------------Paramètres d'entrée


#W = 3e-2            #Largeur de la bouche
#H = 2e-3            #Longueur de la bouche
#gamma_air = 1.4     #Indice adiabatique
#rho = 1.292         #Masse vol air
#Sc = np.pi*rc**2    #section clarinette
#pM = 0.1            #Pression de plaquage statique

#zeta = W*H/Sc*np.sqrt(2*gamma_air*rho/pM)              #Valeur de zeta en fonction des paramètres de la bouche   

#---------------------------------------Méthodes de Runge-Kutta 

def RK1(X,args,vecs):                    #Ordre 1
    dt=1/fs
    func_index=np.array([(x+1)%2 for x in range(nb_mode*2)])    #Vecteur à multiplier avec X pour avoir les non-dérivées uniquement
    
    x2=np.zeros(fs*dur)
    x2[0]=sum(func_index*X)
    for i in range(fs*dur-1):
        Xs=[x*dt for x in funtion(X,args,vecs)]
        X=np.add(X,Xs)
        x2[i+1]=sum(func_index*X)    
    return x2

def RK2(X,args,vecs):                    #Ordre 2
    dt=1/fs
    x2=np.zeros(fs*dur)
    func_index=np.array([(x+1)%2 for x in range(nb_mode*2)])    #Vecteur à multiplier avec X pour avoir les non-dérivées uniquement
    
    x2[0]=sum(func_index*X)
    for i in range(fs*dur-1):
        Xp=[x*dt/2 for x in funtion(X,args,vecs)]
        #print(Xp)
        Xs=[x*dt for x in funtion(np.add(X,Xp),args,vecs)]
        X=np.add(X,Xs)
        #print(Xs)
        x2[i+1]=sum(func_index*X)
    return x2

def RK4(X,args,vecs):                    #Ordre 4
    dt=1/fs
    x2=np.zeros(fs*dur)
    (Fbis,omegabis,Y_mbis,deriv_index,func_index,x_out)=vecs
    x2[0]=sum(func_index*X)
    for i in range(fs*dur-1):
        k1=funtion(X,args,vecs)
        
        k1x=[x*dt/2 for x in k1]
        k2=funtion(np.add(X,k1x),args,vecs)
        
        k2x=[x*dt/2 for x in k2]
        k3=funtion(np.add(X,k2x),args,vecs)
        
        k3x=[x*dt for x in k3]
        k4=funtion(np.add(X,k3x),args,vecs)
        
        k2s=[x*2 for x in k2]
        k3s=[x*2 for x in k3]
        #print(k1)
        Xs=np.add(np.add(np.add(k1,k2s),k3s),k4)
        Xsx=[x*dt/6 for x in Xs]
        X=np.add(X,Xsx)
        #print(Xs)
        x2[i+1]=sum(func_index*X)
    return x2

#---------------------------------------- Définition du système \Dot{X}=f(X)

def funtion(x,args,vecs):
    (Fbis,omegabis,Y_mbis,deriv_index,func_index,x_out) =vecs
    (F,omega,Y_m,v0,vb,Fb)  = args
    
    
    xderiv_index=sum(x*deriv_index)
    xfunc_index=sum(x*func_index)
    #commun=sum(x*deriv_index)*(A+2*B*sum(x*func_index)+3*C*sum(x*func_index)**2) #Spécifique à la clarinette
    #commun=Fb*v0*xderiv_index*(2*vb*xfunc_index-xfunc_index**2+v0**2)/(-2*vb*xfunc_index+xfunc_index**2+v0**2) #Violon par Ollivier
    commun=Fb*np.exp(-sigma*xfunc_index**2)*xderiv_index*(np.sqrt(sigma)*(2.33164-0.00186532*sigma)*xfunc_index**2+0.0127324*mud*np.exp(sigma*xfunc_index**2)+0.000932658*np.sqrt(sigma)-(4.66329+5)*sigma**(3/2)*xfunc_index**4)/(xfunc_index**2+0.0004)
    x_out=np.zeros(nb_mode*2)
    x_out[1:]=Fbis[1:]*commun-(Y_mbis*x)[1:]-(np.power(omegabis,2)*x)[:-1]
    x_out[:-1]=x_out[:-1]+(x*deriv_index)[1:]

    return x_out


#------------------------------------------ Fonction pour jouer le son et enregistrer le wav
def play(y,Fe=44100):
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
        fichier2='C:/Users/GaHoo/Desktop/Cours/ATIAM/9. PAM/Code/son.wav' #Adresse du fichier exporté, à modifier
        sf.write(fichier,z,Fe)
        sf.write(fichier2,z,Fe)     #Ecrit le fichier wav dans le fichier
        os.system(''+fichier+' &')
        
#------------------------------------------------Fonction faisant tourner le modèle
def simulation(dur,nb_mode, fe, gamma, zeta, L,Lb,c,dc,Yc,Fb,vb,fig=False, sound=False):
    
    #------------------------------------------Fréquences
    f=np.zeros(nb_mode)                 #Initialisation générale fréquences des modes
    #Leff=L                             #Cas Clarinette Zs=0
    #Leff=L+(8*rc/(3*np.pi))            #Cas Clarinette bafflée
    #Leff=Lc+0.6*rc                     #Cas Clarinette non bafflée
    #f=np.array([(2*n+1)*c/(4*Leff) for n in range(nb_mode)]) #Cas particulier de la clarinette (quintoie)
    #f = (2*np.arange(nb_mode)+1)*c/(4*Leff)     #Cas particulier de la clarinette (quintoie)
    f=(np.arange(1,nb_mode+1)*np.pi)/(2*L)*np.sqrt(Tc/(rhoc*(np.pi*(dc/2)**2)))*np.sqrt(1+((Ec*Ic/(2*Tc))*(np.arange(1,nb_mode+1)**2*np.pi**2/(L**2)))) #Cas particulier du violon uniquement corde
    """
    f[0] = 220                     #Fréquence premier mode ajustée à la main
    f[1] = 440                     #Fréquence deuxième mode
    f[2] = 660
    f[3] = 880
    f[4] = 1100"""
    omega=f*2*np.pi                  #Conversion freq/puls  
    #------------------------------------------Admittances
    #Y_m=np.ones(nb_mode)*1 /1233.36096998528    #Initialisation de toutes les admittances à une valeur par défaut
    Y_m=1j*Yc*(np.tan(omega/c*Lb)**(-1)+np.tan(omega/c*(L-Lb))**(-1))**(-1) #Valeur par défaut pour le violon
    """
    #Y_m[0] = 1 /1233.36096998528                #Admittance au premier mode ajustée à la main
    #Y_m[1] = 1 /1233.36096998528                #Admittance au deuxième mode
    #Y_m[2] = 1 /1233.36096998528
    """
    #------------------------------------------------Variables calculées
    F=2*c/L*np.arange(1,nb_mode+1)                          #Coefficients modaux
    time = np.linspace(0,dur,fs*dur)                            #Vecteur temps

    
    #A = zeta*(3 * gamma - 1) / 2 /np.sqrt(gamma)            #Paramètres pour l'équation du modèle
    #B = -zeta*(3*gamma+1)/8/gamma**(3/2)
    #C = -zeta*(gamma +1)/16/gamma**(5/2)
    
    #args = (A, B, C,F,omega,Y_m,v0,vb,Fb)                            #Encapsulation des paramètres pour la résolution
    args = (F,omega,Y_m,v0,vb,Fb)                            #Encapsulation des paramètres pour la résolution

    #--------------------------------Vecteurs utiles pour les calculs
    deriv_index = np.arange(nb_mode*2)%2        #Vecteur à multiplier avec X pour avoir les dérivées uniquement
    func_index= (np.arange(nb_mode*2)+1)%2    #Vecteur à multiplier avec X pour avoir les non-dérivées uniquement
    x_out=np.zeros(nb_mode*2)                               
    Fbis=np.zeros(nb_mode*2)                                #Conversion de F pour qu'il fasse la taille nb_mode*2
    Fbis[1::2]=F
    omegabis=np.zeros(nb_mode*2)
    omegabis[::2]=omega
    Y_mbis=np.zeros(nb_mode*2)
    Y_mbis[1::2]=abs(Y_m)
    vecs=(Fbis,omegabis,Y_mbis,deriv_index,func_index,x_out)
    
    #--------------------------------Lancement
    
    t1=tim.time()                   #Démarrage du timer
    #X=gamma*func_index                  #Initialisation de X avec p_n=gamma à l'instant 0
    X=vb*func_index
    p=RK4(X,args,vecs)                   #Appel de la résolution
    tcalc=tim.time()-t1             #Arrêt du timer
    print("Temps de calcul : "+str(tcalc)+"s")
    
    if sound==True:
        play(p)                         #Ecoute du son
        
    
    if fig==True:
        #-----------------------------------------------Plots
        plt.plot(time, p, 'orange', linewidth = 2)
        plt.xlabel('time (s)')
        plt.ylabel('pressure')
        plt.xlim(0,0.5)
        plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
        #plt.ylim(0,0.000000000001)
        plt.xlim()
        plt.grid(True)
        


    
    return p,time


p,time=simulation(dur,nb_mode, fs, gamma, zeta, L,Lb,c,dc,Yc,Fb,vb,fig=True, sound=True)
