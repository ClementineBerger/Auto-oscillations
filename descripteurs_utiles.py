#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 12:32:49 2023

@author: fouilloumalena
"""

"""
Ce script contient les fonctions calculant les descripteurs utiles à la cartographie des régimes d'oscillations'

--------------------

are_there_oscillations : renvoie s'il y a présence d'oscillations entretenues ou non à partir d'un critère donné 
                         en argument
                        
                        
get_f0, f0_to_categorical : renvoie le numéro d'une note harmonique si celle-ci est proche de la vrai fréquence
                            f0. L'écart entre les deux est calculé en 'cents'.
"""

import os
import scipy.io as io
from scipy.io import savemat
import librosa
import librosa.display
import matplotlib
import matplotlib.pyplot as plt
import numpy as np



# Son ou pas son ?
def are_there_oscillations(waveform, epsilon):
    """
    Parameters
    ----------
    waveform = p(t)/v(t) calculé à partir d'un modèle
    epsilon = critère de décision 

    Returns
    -------
    True or False selon la condition : y-a-t-il oscillation ou non ?
    """
    
    N2_3 = int(len(waveform) / 3)                #Intervalle d'observation du signal, choisi au dernier tier du temps de simulation
     
    waveform_ = waveform[N2_3:]                  #Zone du signal à observer

    
    

    waveform_ = waveform_- np.mean(waveform_)     #Centrage en zéro
    waveform_= waveform_/np.max(np.abs(waveform_))       #Normalisation
      
    criterion = np.mean(np.abs(waveform_))       #Calcul de la moyenne du signal  
    '''

    if np.max(waveform_) < 1e-2 : 
        criterion = False
    else : 
    N1 = int(len(waveform)/ 5) #début du signal
    N2 = len(waveform)-N1 #fin du signal
    
    #Calcul du rapport entre début et fin du signal
    criterion = np.abs(np.max(waveform[N2:])/np.max(waveform[:N1]))
    '''
    
    return criterion > epsilon 



#Pitch
def get_f0(waveform, sr, fmin=librosa.note_to_hz("C1"), fmax=librosa.note_to_hz("C3")):
    
    """ 
    Estimate F0 using Yin's algorithm. The algorithm is applied frame by frame
    then the final F0 is obtained using the mean of the last 2/3 frames.
    """
    
    n_1_3 = int(np.rint(len(waveform) / 3))                         #Intervalle d'observation du signal
    f0 = librosa.yin(waveform[n_1_3:], fmin=fmin, fmax=fmax, sr=sr) #Fréquence fondamentale du signal observé
    return np.mean(f0[1:])


def f0_to_categorical(f0, ref_frequencies, epsilon):
    
    """ This function checks whether f0 is close to a frequency in the ref_frequencies
    array, close meaning less than epsilon cents away.

    Args:
        f0 (float): f0 to test
        ref_frequencies (array): Array of reference frequencies to be checked
        epsilon (int): Theshold in cents
    """
    
    n_cents = np.abs(1200 * np.log(f0 / ref_frequencies))           #Écart entre fréquence fondamentale du signal et celles de référence
    idx = np.argmin(n_cents)
    if n_cents[idx] > epsilon:
        return False, None
    else:
        return True, idx

 