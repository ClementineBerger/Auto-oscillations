#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 10:04:51 2023

@author: fouilloumalena
"""
import pandas as pd
from tqdm.auto import tqdm
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as sig
import scipy.integrate as intgr
from modelisation_physique.guide_onde import simulation

def are_there_oscillations(waveform, epsilon):
    N2_3 = int(len(waveform) / 3)
    criterion = np.mean(np.abs(waveform[N2_3:]))
    return criterion > epsilon


#Paramètres (au hasard pour l'instant):
t_max = 0.3 #durée de la simulation en s
fe = 44100 #Fréquence d'échantillonnage
type_reflection = 'dirac' #type de réflexion au bout du guide, 'dirac' ou 'triangle'
#frac_T : #seulement pour le type 'triangle', définition de la demi-largeur du triangle T/frac_T
L =0.6 #Longueur du cylindre
c =340 #célérité des ondes


def classe(parameters):
    parameters = np.array(parameters)
    parameters= pd.DataFrame(parameters, columns = ['gamma','zeta'])
    l= len(parameters)
    # Create sound samples and associated labels
    wave_dataset = np.zeros((l, int(t_max*fe)))
    labels = np.zeros(l)
    mean_amplitude = np.zeros(l)
    
    for i, x in tqdm(parameters.iterrows()):
        waveform, _ =simulation(t_max, fe, x["gamma"], x["zeta"], type_reflection, L, c, frac_T=10 ,fig=False, sound=False)
        wave_dataset[i] = waveform
        n_1_3 = int(len(waveform)/3)
        mean_amplitude[i] = np.mean(np.abs(waveform[n_1_3:]))
        labels[i] = 1 if are_there_oscillations(waveform, epsilon=0.15) else 0
    return labels

labels = classe(parameters)

