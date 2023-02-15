import numpy as np
#from scipy.integrate import odeint


#---------------------------------------Méthodes de Runge-Kutta 

def RK1(X,fe,t_max,deriv_index, func_index,nb_mode,Fbis,Y_mbis,omegabis,args):                    #Ordre 1
    dt=1/fe
    x2=np.zeros(int(fe*t_max))
    x2[0]=X[0]
    for i in range(int(fe*t_max)-1):
        Xs=[x*dt for x in func(X,deriv_index, func_index,nb_mode,Fbis,Y_mbis,omegabis,args)]
        X=np.add(X,Xs)
        x2[i+1]=X[0]     
    return x2

def RK2(X,fe,t_max,deriv_index, func_index,nb_mode,Fbis,Y_mbis,omegabis,args):                    #Ordre 2
    dt=1/fe
    x2=np.zeros(int(fe*t_max))
    x2[0]=X[0]
    for i in range(int(fe*t_max)-1):
        Xp=[x*dt/2 for x in func(X,deriv_index, func_index,nb_mode,Fbis,Y_mbis,omegabis,args)]
        #print(Xp)
        Xs=[x*dt for x in func(np.add(X,Xp),deriv_index, func_index,nb_mode,Fbis,Y_mbis,omegabis,args)]
        X=np.add(X,Xs)
        #print(Xs)
        x2[i+1]=X[0]
    return x2

def RK4(X,fe,t_max,deriv_index, func_index,nb_mode,Fbis,Y_mbis,omegabis,args):                    #Ordre 4
    dt=1/fe
    x2=np.zeros(int(fe*t_max))
    x2[0]=X[0]+X[2]
    for i in range(int(fe*t_max)-1):
        k1=func(X,deriv_index, func_index,nb_mode,Fbis,Y_mbis,omegabis,args)
        
        k1x=[x*dt/2 for x in k1]
        k2=func(np.add(X,k1x),deriv_index, func_index,nb_mode,Fbis,Y_mbis,omegabis,args)
        
        k2x=[x*dt/2 for x in k2]
        k3=func(np.add(X,k2x),deriv_index, func_index,nb_mode,Fbis,Y_mbis,omegabis,args)
        
        k3x=[x*dt for x in k3]
        k4=func(np.add(X,k3x),deriv_index, func_index,nb_mode,Fbis,Y_mbis,omegabis,args)
        
        k2s=[x*2 for x in k2]
        k3s=[x*2 for x in k3]
        #print(k1)
        Xs=np.add(np.add(np.add(k1,k2s),k3s),k4)
        Xsx=[x*dt/6 for x in Xs]
        X=np.add(X,Xsx)
        #print(Xs)
        x2[i+1]=sum(func_index*X)
    return x2

#---------------------------------------- Définition du système \Dot{X}=f(X)

def func(x,deriv_index, func_index,nb_mode,Fbis,Y_mbis,omegabis,args):
    (A, B, C,F,omega,Y_m) = args

    commun=sum(x*deriv_index)*(A+2*B*sum(x*func_index)+3*C*sum(x*func_index)**2)
    
    x_out=np.zeros(nb_mode*2)
    x_out[1:]=Fbis[1:]*commun-(Y_mbis*x)[1:]-(np.power(omegabis,2)*x)[:-1]
    #print(x_out[0])
    #if x_out[1]!=0:
    #    print(x_out)
    x_out[:-1]=x_out[:-1]+(x*deriv_index)[1:]
    #print(x_out[0])

    return x_out



################# SIMULATION ######################

def simulation(gamma, zeta, t_max, fe, nb_mode, L, c):
    #------------------------------------------Admittances
    Y_m=np.ones(nb_mode)*1 /1233.36096998528    #Initialisation de toutes les admittances à une valeur par défaut
    
    #------------------------------------------Fréquences
    Leff = L                            #Cas Clarinette Zs=0
    #Leff=Lc+(8*rc/(3*np.pi))            #Cas Clarinette bafflée
    #Leff=Lc+0.6*rc                      #Cas Clarinette non bafflée
    f = (2*np.arange(nb_mode)+1)*c/(4*Leff)        #Cas particulier de la clarinette (quintoie)
    
    omega = 2*np.pi*f                   # pulsations
    F=np.array([2*x* c / L for x in range(1,nb_mode+1)])   #coefficients modaux
    
    time = np.arange(int(t_max*fe))/fe  # Liste des temps
    
    A = zeta*(3 * gamma - 1) / 2 /np.sqrt(gamma)            #Paramètres pour l'équation du modèle
    B = -zeta*(3*gamma+1)/8/gamma**(3/2)
    C = -zeta*(gamma +1)/16/gamma**(5/2)
    
    args = (A, B, C,F,omega,Y_m)                            #Encapsulation des paramètres pour la résolution
    
    #--------------------------------Vecteurs utiles pour les calculs
    deriv_index = np.array([x%2 for x in range(nb_mode*2)])        #Vecteur à multiplier avec X pour avoir les dérivées uniquement
    func_index = np.array([(x+1)%2 for x in range(nb_mode*2)])    #Vecteur à multiplier avec X pour avoir les non-dérivées uniquement
    print(len(func_index))
    x_out=np.zeros(nb_mode*2)                               
    Fbis=np.zeros(nb_mode*2)                                #Conversion de F pour qu'il fasse la taille nb_mode*2
    Fbis[1::2]=F
    omegabis=np.zeros(nb_mode*2)
    omegabis[::2]=omega
    Y_mbis=np.zeros(nb_mode*2)
    Y_mbis[1::2]=Y_m
    
    X=np.array([gamma*i for i in func_index])     #Initialisation de X avec p_n=gamma à l'instant 0

    p=RK4(X,fe,t_max,deriv_index, func_index,nb_mode,Fbis,Y_mbis,omegabis,args)                   #Appel de la résolution
    
    return p