#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 12:09:24 2023

@author: fouilloumalena
"""
"""

This code takes as arguments a mapping of points (X) and the observed descriptor
('oscillations', 'pitch', 'attack' etc...)
                                                                                                   
It returns an array of labels y of X.

WE NEED TO BE ABLE TO MOVE ON FROM THE ARGUMENTS OF MAT

"""
import descripteurs_utiles as dp
import os
import pandas as pd
from tqdm.auto import tqdm
import numpy as np
import librosa

def labels(X, descriptor, abscisse, 
           ordonnee, modele, instrument, 
           arg_modele, arg_descriptor, note_frequencies
           ):
    
    """
    Parameters
    -------
    X = points du mapping
    
    descriptor : descritpeur que l'on choisit d'observer
    
    abscisse, ordonnée : paramètre du mappping ("gamma/zeta", ou "gamma/longueur" etc...)
    
    modele= fonction de simulation du modele choisit pour le mapping : méthode guide d'onde ou modale
    
    arg_descriptors = arguments des fonctions descripteurs
    
    arg_model = arguments des méthodes
    
    note_frequencies = notes de référence pour la description du pitch
    
    Returns
    -------
    y = tableau contenant la classe de chaque point
    
    """
    
    #Conversion paramètres mat to Python
    t_max, fe, L, c, nb_mode, durete_rampe =  np.array(arg_modele).tolist()
    note_frequencies = np.array(note_frequencies).tolist()
    arg_descriptor= np.array(arg_descriptor).tolist()
    X= pd.DataFrame(np.array(X), columns = [abscisse, ordonnee])   
   
    
    # Create labels
    y = np.zeros(len(X))
    
    #Méthode utilisée
    if modele == 'guide_onde': #Paramètres des méthode
        from modelisation_physique.guide_onde import simulation
    else :
        from modelisation_physique.Modele_modal_fct_rampe import simulation
        
 
    # Descripteur choisit
    if descriptor == "are_there_oscillations": #Paramètres des descripteurs
        epsilon = arg_descriptor
        type_reflection='dirac'
        for i, x in tqdm(X.iterrows()):
            waveform, _ = simulation(x[abscisse], x[ordonnee], t_max, fe, L,  nb_mode, instrument, durete_rampe) 
    
            y[i] = 1 if dp.are_there_oscillations(waveform, epsilon) else 0
        return y
    
    elif descriptor == "pitch" :
        
        n_classes = len(note_frequencies)
        fe ,epsilon ,cents_threshold, zeta = arg_descriptor
        
        for i, x in tqdm(X.iterrows()): 
                waveform, _ = simulation(x[abscisse], zeta , t_max, fe, x[ordonnee], nb_mode, instrument, durete_rampe)

                f0 = dp.get_f0(waveform, fe) * dp.are_there_oscillations(waveform, epsilon)
                is_close, idx = dp.f0_to_categorical(f0, note_frequencies, cents_threshold)
                if is_close:
                    y[i] = idx
                else:
                    y[i] = n_classes
        return y 

y = labels(X, descriptor, abscisse, ordonnee, modele, instrument, arg_modele, arg_descriptor, note_frequencies)


               