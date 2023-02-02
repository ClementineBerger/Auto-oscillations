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

gamma = 0.8

# ------------------------------------------------Paramètres d'entrée

W = 2e-2  # Largeur de la anche de clarinette
H = 6.5e-2  # Longueur de la anche de clarinette
gamma_air = 1.4  # Indice adiabatique
rho = 1.292  # Masse vol air
c = 343  # Vitesse son
rc = 3e-2  # rayon de la clarinette
Lc = 60e-2  # longueur clarinette
Sc = np.pi * rc**2  # section clarinette
pM = 0.1  # Pression de plaquage statique
Y_m1 = 1 / 1233.36096998528  # Admittance au premier mode
Y_m2 = 1 / 1233.36096998528  # Admittance au deuxième mode
f1 = 220  # Fréquence premier mode
f2 = 440  # Fréquence deuxième mode

# ------------------------------------------------Variables générales

fs = 44100  # Fréquence d'échantillonnage


# ------------------------------------------------Variables calculées

omega1 = 2 * np.pi * f1  # Conversion freq/puls
omega2 = 2 * np.pi * f2
F1 = 2 * c / Lc  # Coef. premier mode
F2 = 4 * c / Lc  # Coef. deuxième mode
time = np.linspace(0, 3, fs * 3)  # Vecteur temps

xi = W * H / Sc * np.sqrt(2 * gamma_air * rho / pM)  #
# xi = 2
A = xi * (2 * gamma - 1) / 2 / np.sqrt(gamma)
B = -xi * (3 * gamma - 1) / 8 / gamma ** (3 / 2)
C = -xi * (gamma + 1) / 16 / gamma ** (5 / 2)

gam1 = Y_m1 + Y_m2
gam2 = omega1**2 + omega2**2 + Y_m1 * Y_m2
gam3 = omega1**2 * Y_m2 + omega2**2 * Y_m1
alpha = F1 * omega2**2 + F2 * omega1**2
beta = Y_m1 * F1 + Y_m2 * F2


args = (
    F1,
    F2,
    A,
    B,
    C,
    alpha,
    beta,
    gam1,
    gam2,
    gam3,
    omega1,
    omega2,
)  # Paramètres pour 2 modes

# args = (F1, A, B, C, Y_m1, omega1)

# ------------------------------------------------Fonctions
def update_parameters(*args):
    # @latexify.function(use_math_symbols=True)
    def ODE_NL(x, t):
        # (F1, A, B, C, Y_m, omega) = args #Un mode
        (F1, F2, A, B, C, alpha, beta, gam1, gam2, gam3, omega1, omega2) = args
        # print(x)
        return [
            x[1],
            (x[1] + x[3])
            * F1
            * ((A - Y_m1) + 2 * B * (x[0] + x[2]) + 3 * C * (x[0] + x[2]) ** 2)
            - omega1**2 * x[0],
            x[3],
            (x[1] + x[3])
            * F2
            * ((A - Y_m2) + 2 * B * (x[0] + x[2]) + 3 * C * (x[0] + x[2]) ** 2)
            - omega2**2 * x[2],
        ]

        # return [x[1],x[2],x[3],-(x[3]*gam1+x[2]*gam2+x[1]*(gam3-alpha*(A+2*B*x[0]+3*C*x[0]**2)*x[1]-beta*(x[2]*(A+2*B*x[0]+3*C*x[0]**2)+2*x[1]**2*(B+3*C*x[0]))-(F1+F2)*(x[3]*(A+2*B*x[0]+3*C*x[0]**2)+6*x[1]*x[2]*(B+3*C*x[0])+6*C*x[1]**3))+omega1**2*omega2**2*x[0])]

        # return [x[1],x[2],x[3],-(x[3]*gam1+x[2]*gam2+x[1]*(gam3-alpha*(A+2*B*x[0]+3*C*x[0]**2)-beta*(x[2]*(A+2*B*x[0]+3*C*x[0]**2)+2*x[1]**2*(B+3*C*x[0]))-(F1+F2)*(x[3]*(A+2*B*x[0]+3*C*x[0]**2)+6*x[1]*x[2]*(B+3*C*x[0])+6*C*x[1]**3))+omega1**2*omega2**2*x[0])]

        # return [x[1],x[2],x[3],-(x[3]*gam1+x[2]*gam2+x[1]*(gam3-alpha*(A+2*B*x[0]+3*C*x[0]**2)-beta*(2*B*(x[1]**2+x[0]*x[2])+3*C*(2*x[0]*x[1]**2+x[0]**2*x[2])+A*x[2])-(F1+F2)*(2*B*(3*x[1]*x[2]+x[0]*x[3])+3*C*(2*(x[1]**3)+6*x[0]*x[1]*x[2]+x[0]**2*x[3])+A*x[3]))+omega1**2*omega2**2*x[0])]

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
p_ini = [gamma, 0, gamma, 0]  # Pour deux modes

ED = update_parameters(*args)
p1, dp, p2, dddp = odeint(ED, p_ini, time).T
p = p1 + p2
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
