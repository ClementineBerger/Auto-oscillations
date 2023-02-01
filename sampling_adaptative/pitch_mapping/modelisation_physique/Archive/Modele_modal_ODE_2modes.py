# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 11:10:51 2023

@author: Romain Caron
"""
import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
#%matplotlib inline

import platform
import time
import soundfile as sf
import os
import sounddevice as sd
import tempfile

#------------------------------------------------Contrôle

gamma = 0.8
dur=5;              #Durée de l'enregistrement à produire en secondes 

#------------------------------------------------Paramètres d'entrée

W = 3e-2            #Largeur de la bouche
H = 2e-3         #Longueur de la bouche
gamma_air = 1.4     #Indice adiabatique
rho = 1.292         #Masse vol air
c = 343             #Vitesse son
rc = 3e-2           #rayon de la clarinette
Lc = 60e-2          #longueur clarinette
Sc = np.pi*rc**2    #section clarinette
pM = 0.1            #Pression de plaquage statique
Y_m1 = 1 /1233.36096998528 #Admittance au premier mode
Y_m2 = 1 /1233.36096998528                  #Admittance au deuxième mode
f1 = 220                     #Fréquence premier mode
f2 = 440                     #Fréquence deuxième mode


#------------------------------------------------Variables générales

fs = 44100          #Fréquence d'échantillonnage


#------------------------------------------------Variables calculées

omega1 = (2*np.pi*f1)                     #Conversion freq/puls
omega2 = (2*np.pi*f2)
F1 = 2 * c / Lc                         #Coef. premier mode
F2 = 4 * c / Lc                         #Coef. premier mode
t = np.linspace(0,dur,fs*dur)            #Vecteur temps
p_ini = [gamma, 0]

zeta = W*H/Sc*np.sqrt(2*gamma_air*rho/pM) #
#zeta = 2
A = zeta*(3 * gamma - 1) / 2 /np.sqrt(gamma)
B = -zeta*(3*gamma+1)/8/gamma**(3/2)
C = -zeta*(gamma +1)/16/gamma**(5/2)

gam1=Y_m1+Y_m2;
gam2=(omega1**2+omega2**2+Y_m1*Y_m2);
gam3=(omega1**2*Y_m2+omega2**2*Y_m1);
alpha=F1*omega2**2+F2*omega1**2
beta=Y_m1*F2+Y_m2*F1


args = (F1,F2, A, B, C,alpha,beta,gam1,gam2,gam3,omega1,omega2) #Paramètres pour 2 modes
#args = (F1, A, B, C, Y_m, omega) #Paramètres pour 1 mode

#------------------Méthodes de Runge-Kutta 
def RK1(X,args):
    dt=1/fs
    x2=np.zeros(fs*dur)
    x2[0]=X[0]
    for i in range(fs*dur-1):
        Xs=[x*dt for x in funtion(X,args)]
        X=np.add(X,Xs)
        x2[i+1]=X[0]     
    return x2

def RK2(X,args):
    dt=1/fs
    x2=np.zeros(fs*dur)
    x2[0]=X[0]
    for i in range(fs*dur-1):
        Xp=[x*dt/2 for x in funtion(X,args)]
        #print(Xp)
        Xs=[x*dt for x in funtion(np.add(X,Xp),args)]
        X=np.add(X,Xs)
        #print(Xs)
        x2[i+1]=X[0]
    return x2

def RK4(X,args):
    dt=1/fs
    x2=np.zeros(fs*dur)
    x2[0]=X[0]
    for i in range(fs*dur-1):
        k1=funtion(X,args)
        k1x=[x*dt/2 for x in k1]
        k2=funtion(np.add(X,k1x),args)
        k2x=[x*dt/2 for x in k2]
        k3=funtion(np.add(X,k2x),args)
        k3x=[x*dt for x in k3]
        k4=funtion(np.add(X,k3x),args)
        k2s=[x*2 for x in k2]
        k3s=[x*2 for x in k3]
        #print(k1)
        Xs=np.add(np.add(np.add(k1,k2s),k3s),k4)
        Xsx=[x*dt/6 for x in Xs]
        X=np.add(X,Xsx)
        #print(Xs)
        x2[i+1]=X[0]
    return x2

def funtion(X,args):
    #(F1, A, B, C, Y_m, omega) = args # Paramètres pour 1 mode
    #X2=[X[1], X[1]*F1*((A-Y_m1)+2*B*X[0]+3*C*X[0]**2) - omega1**2*X[0]] #Fonction pour un mode
    
    
    (F1,F2, A, B, C,alpha,beta,gam1,gam2,gam3,omega1,omega2) = args
    #X2=[X[1],X[2],X[3],-(X[3]*gam1+X[2]*gam2+X[1]*(gam3-alpha*(A+2*B*X[0]+3*C*X[0]**2)-beta*(2*B*(X[1]**2+X[0]*X[2])+3*C*(2*X[0]*X[1]**2+X[0]**2*X[2])+A*X[2])-(F1+F2)*(2*B*(3*X[1]*X[2]+X[0]*X[3])+3*C*(2*(X[1]**3)+6*X[0]*X[1]*X[2]+X[0]**2*X[3])+A*X[3]))+omega1**2*omega2**2*X[0])]
    X2=[X[1],X[2],X[3],-(X[3]*gam1+X[2]*gam2+X[1]*(gam3-alpha*(A+2*B*X[0]+3*C*X[0]**2)*X[1]-beta*(X[2]*(A+2*B*X[0]+3*C*X[0]**2)+2*X[1]**2*(B+3*C*X[0]))-(F1+F2)*(X[3]*(A+2*B*X[0]+3*C*X[0]**2)+6*X[1]*X[2]*(B+3*C*X[0])+6*C*X[1]**3))+omega1**2*omega2**2*X[0])]
    
    return X2


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
        
#------------------------------------------------Moteur

t1=time.time()
#X=np.array([gamma,0.1]) #Pour un mode
X=np.array([gamma,0.1,0.1,0.1]) #Pour deux modes
p=RK4(X,args)
tcalc=time.time()-t1
print("Temps de calcul : "+str(tcalc)+"s")
play(p)

plt.plot(t, p, 'orange', linewidth = 2)
plt.xlabel('time (s)')
plt.ylabel('pressure')
plt.xlim(0,0.5)
plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
#plt.ylim(0,0.000000000001)
plt.xlim()
plt.grid(True)

