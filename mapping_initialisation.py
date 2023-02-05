#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 13:54:34 2023

@author: fouilloumalena
"""

"""

Ce script contient une fonction permettant d'initialiser les points 
dans un espace de taille donné 

"""
import numpy as np
from doepy import build

def initialisation(
        abscisse, ordonnée,dim1 ,dim2, 
        num_samples):
    """
    abscisse = paramètre de contrôle en abscisse
    ordonnée = paramètre de contrôle en ordonnée
    dim1= taille de la première dimension
    dim2= taille de la deuxième dimension

    """
    num_samples = int(num_samples)
    dim1= np.array(dim1)
    dim2= np.array(dim2)
    return build.space_filling_lhs({abscisse: dim1, ordonnée: dim2},num_samples=num_samples).to_numpy()

X = initialisation(abscisse, ordonnee,dim1 ,dim2, num_samples)

