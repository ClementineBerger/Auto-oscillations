#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 12:32:49 2023

@author: fouilloumalena
"""

"""
Ce script contient les fonctions calculant les descripteurs utiles au mapping

----------
are_there_oscillations : renvoie s'il y a présence d'oscillations entretenues ou non à partir d'un critère donné 
                         en argument
                        
                        
get_f0, f0_to_categorical : renvoie le numéro d'une note harmonique si celle-ci est proche de la vrai fréquence
                            f0.
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
    waveform = p(t) calculé à partir d'un modèle
    arg_d = critère de décision

    Returns
    -------
    True or False selon la condition : y-a-t-il oscillation ou non ?
    """
    
    N2_3 = int(len(waveform) / 3)
    criterion = np.mean(np.abs(waveform[N2_3:]))
    return criterion > epsilon



#Pitch
def get_f0(waveform, sr, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7")):
    """ Estimate F0 using Yin's algorithm. The algorithm is applied frame by frame
    then the final F0 is obtained using the mean of the last 2/3 frames."""
    n_1_3 = int(np.rint(len(waveform) / 3))
    f0 = librosa.yin(waveform[n_1_3:], fmin=fmin, fmax=fmax, sr=sr)
    return np.mean(f0[1:])


def f0_to_categorical(f0, ref_frequencies, epsilon):
    """ This function checks whether f0 is close to a frequency in the ref_frequencies
    array, close meaning less than epsilon cents away.

    Args:
        f0 (float): f0 to test
        ref_frequencies (array): Array of reference frequencies to be checked
        epsilon (int): Theshold in cents
    """
    n_cents = np.abs(1200 * np.log(f0 / ref_frequencies))
    idx = np.argmin(n_cents)
    if n_cents[idx] > epsilon:
        return False, None
    else:
        return True, idx

 