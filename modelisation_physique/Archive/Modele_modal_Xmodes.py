# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 09:20:08 2023

@author: Romain Caron
"""
# ------------------------------------------------Import

import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

#%matplotlib inline

import platform
import soundfile as sf
import os
import sounddevice as sd
import tempfile

# from ODE.py import *

# ------------------------------------------------Contrôle

gamma = 0.6
zeta = 0.5

# ------------------------------------------------Paramètres d'entrée

nb_mode = 3
W = 3e-2  # Largeur de la bouche
H = 2e-3  # Longueur de la bouche
gamma_air = 1.4  # Indice adiabatique
rho = 1.292  # Masse vol air
c = 343  # Vitesse son
rc = 3e-2  # rayon de la clarinette
Lc = 60e-2  # longueur clarinette
Sc = np.pi * rc**2  # section clarinette
pM = 0.1  # Pression de plaquage statique
Y_m = np.ones(nb_mode) * 1 / 1233.36096998528
Y_m[0] = 1 / 1233.36096998528  # Admittance au premier mode
# Y_m[1] = 1 /1233.36096998528                  #Admittance au deuxième mode
# Y_m[2] = 1 /1233.36096998528

f = np.zeros(nb_mode)  # Initialisation générale fréquences des modes
Leff = Lc  # Cas Clarinette Zs=0
Leff = Lc + (8 * rc / (3 * np.pi))  # Cas Clarinette bafflée
# Leff=Lc+0.6*rc #Cas Clarinette non bafflée
f = np.array(
    [(2 * n + 1) * c / (4 * Leff) for n in range(nb_mode)]
)  # Cas particulier de la clarinette
"""
f[0] = 220                     #Fréquence premier mode ajustée à la main
f[1] = 440                     #Fréquence deuxième mode
f[2] = 660
f[3] = 880
f[4] = 1100"""
# ------------------------------------------------Variables générales

fs = 44100  # Fréquence d'échantillonnage


# ------------------------------------------------Variables calculées
omega = np.array([x * 2 * np.pi for x in f])  # Conversion freq/puls
F = np.array([2 * x * c / Lc for x in range(1, nb_mode + 1)])  # Coefficients modaux
time = np.linspace(0, 3, fs * 3)  # Vecteur temps

# zeta = W*H/Sc*np.sqrt(2*gamma_air*rho/pM) #Paramètres pour l'équation du modèle
A = zeta * (3 * gamma - 1) / 2 / np.sqrt(gamma)
B = -zeta * (3 * gamma + 1) / 8 / gamma ** (3 / 2)
C = -zeta * (gamma + 1) / 16 / gamma ** (5 / 2)


args = (A, B, C, F, omega, Y_m)

# --------------------------------Vecteurs utiles pour les calculs
deriv_index = np.array(
    [x % 2 for x in range(nb_mode * 2)]
)  # Vecteur à multiplier avec X pour avoir les dérivées uniquement
func_index = np.array(
    [(x + 1) % 2 for x in range(nb_mode * 2)]
)  # Vecteur à multiplier avec X pour avoir les non-dérivées uniquement
# x_out=np.zeros(nb_mode*2)
Fbis = np.zeros(nb_mode * 2)  # Conversion de F pour qu'il fasse la taille nb_mode*2
Fbis[1::2] = F
omegabis = np.zeros(nb_mode * 2)
omegabis[::2] = omega
Y_mbis = np.zeros(nb_mode * 2)
Y_mbis[1::2] = Y_m
# ------------------------------------------------Fonctions
def update_parameters(*args):
    def ODE_NL(x, t):
        (A, B, C, F, omega, Y_m) = args

        commun = sum(x * deriv_index) * (
            A + 2 * B * sum(x * func_index) + 3 * C * sum(x * func_index) ** 2
        )
        x_out = np.zeros(nb_mode * 2)
        x_out[1:] = (
            Fbis[1:] * commun - (Y_mbis * x)[1:] - (np.power(omegabis, 2) * x)[:-1]
        )
        x_out[:-1] = x_out[:-1] + (x * deriv_index)[1:]

        # [X[1], F1*(X[1]+X[3])*(A+2*B*(X[0]+X[2])+3*C*(X[0]+X[2])**2)-Y_m1*X[1]- omega1**2*X[0]

        return x_out

    return ODE_NL


def play(y, Fe=44100):
    rep = 1
    z = np.real(y) / (abs(np.real(y)).max())
    if (
        platform.system() == "Darwin"
    ):  # MAC (sous linux sounddevice a un comportement erratique)
        sd.play(z, Fe)
        return
    fichier = tempfile.mktemp() + "SON_TP.wav"
    sec = len(y) / Fe
    if sec <= 20:
        rep = True
    if sec > 20:
        print("Vous allez créer un fichier son de plus de 20 secondes.")
        rep = None
        while rep is None:
            x = input("Voulez-vous continuer? (o/n)")
            if x == "o":
                rep = True
            if x == "n":
                rep = False
            if rep is None:
                print("Répondre par o ou n, merci. ")
    if rep:
        fichier2 = "C:/Users/GaHoo/Desktop/Cours/ATIAM/9. PAM/Code/son.wav"  # Adresse du fichier exporté, à modifier
        sf.write(fichier, z, Fe)
        sf.write(fichier2, z, Fe)  # Ecrit le fichier wav dans le fichier
        os.system("" + fichier + " &")


# ------------------------------------------------Moteur

# p_ini = [gamma, 0] #Pour un mode
# p_ini = [gamma, 0,gamma,0] # Pour deux modes
p_ini = [gamma * i for i in func_index]


ED = update_parameters(*args)
y = odeint(ED, p_ini, time).T
p = func_index @ y
# ------------------------------------------------Affichage

plt.plot(time, p * 10000000, "orange", linewidth=2)
plt.xlabel("time (s)")
plt.ylabel("pressure")
plt.xlim(0, 0.5)
plt.ticklabel_format(style="sci", axis="x", scilimits=(0, 0))
# plt.ylim(0,0.000000000001)
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
