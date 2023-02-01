#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 29 14:59:22 2023

@author: fouilloumalena
"""
import pandas as pd
import os
import scipy.io as io
from scipy.io import savemat
import librosa
import librosa.display
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from doepy import build
from mpl_toolkits.axes_grid1 import ImageGrid
from sklearn.inspection import DecisionBoundaryDisplay
from sklearn.svm import SVC
from tqdm.auto import tqdm
from modelisation_physique.mvt_Helmholtz import simulation

def are_there_oscillations(waveform, epsilon):
    N2_3 = int(len(waveform) / 3)
    criterion = np.mean(np.abs(waveform[N2_3:]))
    return criterion > epsilon


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

#paramètres 
sim_length = 0.3
sample_rate = 22050
celerity = 340
osc_threshold = 0.15  # threshold to decide whether there are oscillations or not
cents_threshold = 15
l2_penalty = 1e6  # L2 Penalty for the SVM optimization
epsilon_length = 0.05  # meters
#Full octave from C0 to B0
note_frequencies = [65.41, 69.3, 73.42, 77.78, 82.41, 87.31, 92.5, 98, 103.83, 110, 116.54, 123.47]
length_min = celerity / (4 * note_frequencies[-1]) - epsilon_length
length_max = celerity / (4 * note_frequencies[0]) + epsilon_length
zeta = 0.5

def classe(parameters):
    
    parameters = np.array(parameters)
    parameters= pd.DataFrame(parameters, columns = ['gamma','length_cylinder'])
    l= len(parameters)
    n_classes = len(note_frequencies)
    labels = np.zeros(l)
    mean_amplitude = np.zeros(l)
    
    for i, x in tqdm(parameters.iterrows()):
        waveform, _ = simulation(sim_length, sample_rate, x["gamma"], zeta, x["length_cylinder"], celerity)
        f0 = get_f0(waveform, sample_rate) * are_there_oscillations(waveform, osc_threshold)
        is_close, idx = f0_to_categorical(f0, note_frequencies, epsilon=cents_threshold)
        if is_close:
            labels[i] = idx
        else:
            labels[i] = n_classes
        #Pour note 0
    for i in range(len(labels)):
        if labels[i] !=3.:
            labels[i] =0
    return labels

labels = classe(parameters)
