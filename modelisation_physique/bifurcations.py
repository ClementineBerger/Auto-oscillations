# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 10:29:57 2023

@author: GaHoo
"""

import numpy as np
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt
import librosa

import Modele_modal_fct_rampe #Importer le modèle à analyser

plt.close(100)

#------------------------------------------------------Paramètres
sample_rate=44100           #Fréquence d'echt
tmax=0.5                     #Durée de chaque simulation
zeta_force=0.8              #Valeur de zeta ou de la force d'excitation
gamma_min=0;                #Première valeur de gamma / vitesse
gamma_max=2;                #Dernière valeur de gamma / vitesse
gamma_step=0.03;            #Pas de gamma / vitesse


#------------------------------------------------------Initialisation
gammas_bif=np.arange(gamma_min,gamma_max,gamma_step) 
f_sortie=np.zeros(len(gammas_bif))
i=0
#------------------------------------------------------Boucle sur gamma/vitesse
for g in gammas_bif:                                
    p,time = Modele_modal_fct_rampe.simulation(tmax=tmax,nb_mode=5,instrument='clarinette', sample_rate=sample_rate, gamma_velo=g, zeta_force=zeta_force,durete_rampe=2000, l_resonateur=60e-2,fig=False, sound=False) #Lancement du modèle désiré
    p[abs(p) < 1e-5] = 1e-5; #Seuillage pour ne pas prendre en compte les oscillations à très faible amplitude
    maxima = argrelextrema(p[int(len(p)-sample_rate*0.1*tmax):], np.greater, order =15) #Obtention des maxima
    
    if maxima[0].size>0: #Si il existe au moins un maximum
        f_sortie[i]=librosa.yin(p,fmin=0.5,fmax=20000,sr=44100)[-1] #Algorithme de Yin pour obtenir la fréquence fondamentale
    i=i+1
    
#-------------------------------------------------------Plots
plt.figure(100)
plt.plot(gammas_bif,f_sortie)
plt.xlabel('Gamma')
plt.ylabel('Frequency (Hz)')
#plt.xlim(0,0.5)
plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
#plt.ylim(0,0.000000000001)
plt.grid(True)
