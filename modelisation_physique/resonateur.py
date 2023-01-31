# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 15:33:03 2023

@author: Romain Caron
"""
import numpy as np
import matplotlib.pyplot as plt
#------------------------Violon 2 ddl cavité
c=340;          #Vitesse son
kp=400;           #Raideur
rho=1.2;
rhop=700;       #Masse vol bois
gamh=1000;       #Amortissement air
gamp=5000;       #Amortissement table harmonie
Ah=2*0.10*0.01; #Aire air
Ap=0.3*0.2;     #Aire table d'harmonie
V=Ap*0.03;         #Volume cavité
mu=rho*c**2/V;
mh=(V*rho)
mp=(Ap*rhop*2e-3)

#-----------------------Variables calculées
omega_h=np.sqrt(mu*Ah**2/mh);
omega_a=np.sqrt(mu*Ap**2/mp)
omega_p=np.sqrt((kp+mu*Ap**2)/mp)
omega_ph=np.sqrt(omega_a*omega_h)

omega=np.array([w for w in range(20,20000)])

#--------------------------------------Code
Dc=(omega_p**2-omega**2+1j*omega*gamp)*(omega_h**2-omega**2+1j*omega*gamh)

Y1=1j*omega*Ap*omega_h**2/(mp*Ah*Dc)
y1=np.fft.ifft(Y1)
#--------------------------------------Plots
plt.plot(omega,Y1)

#end=np.convolve(y1,p)
#play(end)