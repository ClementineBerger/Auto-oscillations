# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 09:20:08 2023

@author: Romain Caron
"""
#------------------------------------------------Import

import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
#%matplotlib inline

import platform
import soundfile as sf
import os
import sounddevice as sd
import tempfile

#from ODE.py import *

#------------------------------------------------Contrôle

gamma = 0.8

#------------------------------------------------Paramètres d'entrée

nb_mode=3;
W = 3e-2            #Largeur de la bouche
H = 2e-3            #Longueur de la bouche
gamma_air = 1.4     #Indice adiabatique
rho = 1.292         #Masse vol air
c = 343             #Vitesse son
rc = 3e-2           #rayon de la clarinette
Lc = 60e-2          #longueur clarinette
Sc = np.pi*rc**2    #section clarinette
pM = 0.1            #Pression de plaquage statique
Y_m=np.zeros(nb_mode)
Y_m[0] = 1 /1233.36096998528 #Admittance au premier mode
Y_m[1] = 1 /1233.36096998528                  #Admittance au deuxième mode
Y_m[2] = 1 /1233.36096998528
f=np.zeros(nb_mode)
f[0] = 220                     #Fréquence premier mode
f[1] = 440                     #Fréquence deuxième mode
f[2] = 660
#------------------------------------------------Variables générales

fs = 44100          #Fréquence d'échantillonnage


#------------------------------------------------Variables calculées
omega=np.array([x*2*np.pi for x in f])           #Conversion freq/puls
F=np.array([2*x* c / Lc for x in range(1,nb_mode+1)]) #Coefficients modaux
time = np.linspace(0,3,fs*3)            #Vecteur temps

zeta = W*H/Sc*np.sqrt(2*gamma_air*rho/pM) #
#zeta = 2
A = zeta*(3 * gamma - 1) / 2 /np.sqrt(gamma)
B = -zeta*(3*gamma+1)/8/gamma**(3/2)
C = -zeta*(gamma +1)/16/gamma**(5/2)


args = (A, B, C,F,omega,Y_m)

#------------------------------------------------Fonctions
def update_parameters(*args):
    def ODE_NL(x, t):
        (A, B, C,F1,F2,omega1,omega2,Y_m1,Y_m2) = args
        return [x[1], (x[1]+x[3])*F1*((A-Y_m1)+2*B*(x[0]+x[2])+3*C*(x[0]+x[2])**2) - omega1**2*x[0],x[3],(x[1]+x[3])*F2*((A-Y_m2)+2*B*(x[0]+x[2])+3*C*(x[0]+x[2])**2) - omega2**2*x[2]]
    return ODE_NL

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

#p_ini = [gamma, 0] #Pour un mode
p_ini = [gamma, 0,gamma,0] # Pour deux modes

ED = update_parameters(*args)
p1, dp,p2,dddp = odeint(ED, p_ini, time).T
p=p1+p2;
#------------------------------------------------Affichage

plt.plot(time, p*10000000, 'orange', linewidth = 2)
plt.xlabel('time (s)')
plt.ylabel('pressure')
plt.xlim(0,0.5)
plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
#plt.ylim(0,0.000000000001)
plt.xlim()
plt.grid(True)

"""
plt.figure()
plt.plot(np.fft.fftshift(np.fft.fftfreq(len(p)))*fs,np.fft.fftshift(np.abs(np.fft.fft(p))))
plt.xlim(0,2000)
plt.xlabel("Fréquence (hz)")
plt.ylabel("Amplitude")
plt.grid()
plt.title("Transformée de fourier de notre signal")
plt.show()
"""

play(p)

