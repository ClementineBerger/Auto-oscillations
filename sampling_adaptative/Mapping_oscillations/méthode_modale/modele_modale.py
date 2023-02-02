#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 10:27:13 2023

@author: fouilloumalena
"""
import pandas as pd
import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
import platform
import time as tim
import os
import tempfile
from modelisation_physique.Modele_modal_ODE_Xmodes import simulation
from tqdm.auto import tqdm

#------------------------------------------------Paramètres d'entrée

nb_mode=3;          #Nombre de modes à modéliser
dur=0.3;              #Durée de l'enregistrement à produire en secondes 
W = 3e-2            #Largeur de la bouche
H = 2e-3            #Longueur de la bouche
gamma_air = 1.4     #Indice adiabatique
rho = 1.292         #Masse vol air
c = 343             #Vitesse son
rc = 3e-2           #rayon de la clarinette
Lc = 0.6         #longueur clarinette
Sc = np.pi*rc**2    #section clarinette
pM = 0.1            #Pression de plaquage statique

#------------------------------------------Admittances
Y_m=np.ones(nb_mode)*1 /1233.36096998528    #Initialisation de toutes les admittances à une valeur par défaut
Y_m[0] = 1 /1233.36096998528                #Admittance au premier mode
Y_m[1] = 1 /1233.36096998528                #Admittance au deuxième mode
#Y_m[2] = 1 /1233.36096998528

#------------------------------------------Fréquences

f=np.zeros(nb_mode)                 #Initialisation générale fréquences des modes
Leff=Lc                             #Cas Clarinette Zs=0
Leff=Lc+(8*rc/(3*np.pi))            #Cas Clarinette bafflée
#Leff=Lc+0.6*rc                     #Cas Clarinette non bafflée
f=np.array([(2*n+1)*c/(4*Leff) for n in range(nb_mode)]) #Cas particulier de la clarinette (quintoie)
"""
f[0] = 220                     #Fréquence premier mode ajustée à la main
f[1] = 440                     #Fréquence deuxième mode
f[2] = 660
f[3] = 880
f[4] = 1100"""
#------------------------------------------------Variables générales

fs = 44100          #Fréquence d'échantillonnage


#------------------------------------------------Variables calculées
omega=np.array([x*2*np.pi for x in f])                  #Conversion freq/puls
F=np.array([2*x* c / Lc for x in range(1,nb_mode+1)])   #Coefficients modaux
time = np.linspace(0,3,fs*3)                            #Vecteur temps


def are_there_oscillations(waveform, epsilon):
    N2_3 = int(len(waveform) / 3)
    criterion = np.mean(np.abs(waveform[N2_3:]))
    return criterion > epsilon


# Calcul des labels : 
def classe(parameters):
    #Calcul des labels
    parameters = np.array(parameters)
    parameters= pd.DataFrame(parameters, columns = ['gamma','zeta'])
    l= len(parameters)
    labels = np.zeros(l)
    mean_amplitude = np.zeros(l)
    # Create sound samples and associated labels
    wave_dataset = np.zeros((l, 132300))

        
    for i, x in tqdm(parameters.iterrows()):
        #Définition des paramètres : 
        waveform= simulation( x["gamma"], x["zeta"])
        n_1_3 = int(len(waveform)/3)
        mean_amplitude[i] = np.mean(np.abs(waveform[n_1_3:]))
        labels[i] = 1 if are_there_oscillations(waveform, epsilon=0.15) else 0

    return labels

labels = classe(parameters)

