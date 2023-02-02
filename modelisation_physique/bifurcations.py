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

fs=44100
tmax=1
zeta=0.8

gammas_bif=np.arange(8,20,1)
f_sortie=np.zeros(len(gammas_bif))
i=0
for g in gammas_bif:                                
    p,time = Modele_modal_fct_rampe.simulation(dur=tmax,nb_mode=2, fs=fs, gamma=g, zeta=zeta, L=60e-2,c=340,rc=2e-2,fig=False, sound=False) #Simulation
    p[abs(p) < 1e-5] = 1e-5;
    result = argrelextrema(p[int(len(p)-fs*0.1*tmax):], np.greater, order =15) #Obtention des maxima
    
    if result[0].size>0:
        #f_sortie[i]=1/((result[0][-1]-result[0][0])/((len(result[0])-1)*fs)) #Calcul de la fréquence et stockage
        f_sortie[i]=librosa.yin(p,fmin=0.5,fmax=20000,sr=44100)[-1]
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
