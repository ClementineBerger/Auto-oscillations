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

gamma = 0.5

#------------------------------------------------Paramètres d'entrée

W = 2e-2            #Largeur de la anche de clarinette
H = 6.5e-2          #Longueur de la anche de clarinette
gamma_air = 1.4     #Indice adiabatique
rho = 1.292         #Masse vol air
c = 343             #Vitesse son
rc = 3e-2           #rayon de la clarinette
Lc = 60e-2          #longueur clarinette
Sc = np.pi*rc**2    #section clarinette
pM = 0.1            #Pression de plaquage statique
Y_m = 1 /1233.36096998528 #Admittance premier mode
f = 220                     #Fréquence premier mode


#------------------------------------------------Variables générales

fs = 44100          #Fréquence d'échantillonnage


#------------------------------------------------Variables calculées

omega = (2*np.pi*f)                     #Conversion freq/puls
F1 = 2 * c / Lc                         #Coef. premier mode
time = np.linspace(0,3,fs*3)            #Vecteur temps
p_ini = [gamma, 0]

xi = W*H/Sc*np.sqrt(2*gamma_air*rho/pM) #
#xi = 2
A = xi*(2 * gamma - 1) / 2 /np.sqrt(gamma)
B = -xi*(3*gamma-1)/8/gamma**(3/2)
C = -xi*(gamma +1)/16/gamma**(5/2)
args = (F1, A, B, C, Y_m, omega)

#------------------------------------------------Fonctions
def update_parameters(*args):
    #@latexify.function(use_math_symbols=True)
    def ODE_NL(x, t):
        (F1, A, B, C, Y_m, omega) = args
        #print(x)
        return [x[1], x[1]*F1*((A-Y_m)+2*B*x[0]+3*C*x[0]**2) - omega**2*x[0]]
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

ED = update_parameters(*args)
p, dp = odeint(ED, p_ini, time).T

#------------------------------------------------Affichage

plt.plot(time, p*100, 'orange', linewidth = 2)
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

