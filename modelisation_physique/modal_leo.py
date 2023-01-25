import os
import platform
import tempfile
import time

import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
import soundfile as sf
from scipy import integrate

# ------------------------------------------------Contrôle
gamma = 0.8
length_simulation = 5  # Durée de l'enregistrement à produire en secondes

# ------------------------------------------------Paramètres d'entrée
W = 3e-2  # Largeur de la bouche
H = 2e-3  # Longueur de la bouche
gamma_air = 1.4  # Indice adiabatique
rho = 1.292  # Masse vol air
# c = 343  # Vitesse son
rc = 3e-2  # rayon de la clarinette
# length_cylinder = 60e-2  # longueur clarinette
Sc = np.pi * rc**2  # section clarinette
pM = 0.1  # Pression de plaquage statique
Y_m1 = 1 / 1233.36096998528  # Admittance au premier mode
Y_m2 = 1 / 1233.36096998528  # Admittance au deuxième mode
f1 = 220  # Fréquence premier mode
f2 = 444  # Fréquence deuxième mode

# ------------------------------------------------Variables générales
# sample_rate = 44100  # Fréquence d'échantillonnage


# ------------------Méthodes de Runge-Kutta
def runge_kutta_1(X, model_args, length_simulation, sample_rate):
    dt = 1 / sample_rate
    x2 = np.zeros(int(sample_rate * length_simulation))
    x2[0] = X[0]
    for i in range(int(sample_rate * length_simulation) - 1):
        Xs = [x * dt for x in state_function(X, model_args)]
        X += Xs
        x2[i + 1] = X[0]
    return x2


def runge_kutta_2(state_vector, model_args, length_simulation, sample_rate):
    dt = 1 / sample_rate
    x2 = np.zeros(int(sample_rate * length_simulation))
    x2[0] = state_vector[0]
    for i in range(int(sample_rate * length_simulation) - 1):
        Xp = [x * dt / 2 for x in state_function(state_vector, model_args)]
        # print(Xp)
        Xs = [x * dt for x in state_function(np.add(state_vector, Xp), model_args)]
        state_vector = np.add(state_vector, Xs)
        # print(Xs)
        x2[i + 1] = state_vector[0]
    return x2


def runge_kutta_4(X, model_args, length_simulation, sample_rate):
    dt = 1 / sample_rate
    x2 = np.zeros(int(sample_rate * length_simulation))
    x2[0] = X[0]
    for i in range(int(sample_rate * length_simulation) - 1):
        k1 = state_function(X, model_args)
        k1x = [x * dt / 2 for x in k1]
        k2 = state_function(np.add(X, k1x), model_args)
        k2x = [x * dt / 2 for x in k2]
        k3 = state_function(np.add(X, k2x), model_args)
        k3x = [x * dt for x in k3]
        k4 = state_function(np.add(X, k3x), model_args)
        k2s = [x * 2 for x in k2]
        k3s = [x * 2 for x in k3]
        # print(k1)
        Xs = np.add(np.add(np.add(k1, k2s), k3s), k4)
        Xsx = [x * dt / 6 for x in Xs]
        X = np.add(X, Xsx)
        # print(Xs)
        x2[i + 1] = X[0] + X[2]
    return x2


def state_function(state_vector, model_args):
    """Function so that \dotX = F[X] in a state-space representation, with
    X being the state vector.
    """
    # (F1, A, B, C, Y_m, omega) = args # Paramètres pour 1 mode
    # X2=[X[1], X[1]*F1*((A-Y_m1)+2*B*X[0]+3*C*X[0]**2) - omega1**2*X[0]] #Fonction pour un mode

    F1, F2, A, B, C, omega1, omega2 = model_args
    deric_state_vector = [
        state_vector[1],
        (state_vector[1] + state_vector[3])
        * F1
        * (
            (A - Y_m1)
            + 2 * B * (state_vector[0] + state_vector[2])
            + 3 * C * (state_vector[0] + state_vector[2]) ** 2
        )
        - omega1**2 * state_vector[0],
        state_vector[3],
        (state_vector[1] + state_vector[3])
        * F2
        * (
            (A - Y_m2)
            + 2 * B * (state_vector[0] + state_vector[2])
            + 3 * C * (state_vector[0] + state_vector[2]) ** 2
        )
        - omega2**2 * state_vector[2],
    ]
    return deric_state_vector


def run_simulation(length_simulation, sample_rate, gamma, zeta, length_cylinder, c):
    state_vector = np.array([gamma, 0.1, gamma, 0.1])  # Pour deux modes
    omega1 = 2 * np.pi * f1  # Conversion freq/puls
    omega2 = 2 * np.pi * f2
    F1 = 2 * c / length_cylinder  # Coef. premier mode
    F2 = 4 * c / length_cylinder  # Coef. premier mode

    A = zeta * (3 * gamma - 1) / 2 / np.sqrt(gamma)
    B = -zeta * (3 * gamma + 1) / 8 / gamma ** (3 / 2)
    C = -zeta * (gamma + 1) / 16 / gamma ** (5 / 2)

    model_args = (
        F1,
        F2,
        A,
        B,
        C,
        omega1,
        omega2,
    )  # Paramètres pour 2 modes

    waveform = runge_kutta_4(state_vector, model_args, length_simulation, sample_rate)
    return waveform


def play(y, Fe=44100):
    rep = 1
    z = np.real(y) / (abs(np.real(y)).max())
    if (
        platform.system() == "Darwin"
    ):  # MAC (sous linux sounddevice a un comportement erratique)
        sd.play(z, Fe)
        return
    fichier = tempfile.mktemp() + "SON_TP.wav"
    sec = len(y) / Fe
    if sec <= 20:
        rep = True
    if sec > 20:
        print("Vous allez créer un fichier son de plus de 20 secondes.")
        rep = None
        while rep is None:
            x = input("Voulez-vous continuer? (o/n)")
            if x == "o":
                rep = True
            if x == "n":
                rep = False
            if rep is None:
                print("Répondre par o ou n, merci. ")
    if rep:
        fichier2 = "C:/Users/GaHoo/Desktop/Cours/ATIAM/9. PAM/Code/son.wav"  # Adresse du fichier exporté, à modifier
        sf.write(fichier, z, Fe)
        sf.write(fichier2, z, Fe)  # Ecrit le fichier wav dans le fichier
        os.system("" + fichier + " &")


# ------------------------------------------------Moteur
if __name__ == "__main__":
    # ours
    t1 = time.time()
    sample_rate = 44100
    zeta = W*H/Sc*np.sqrt(2*gamma_air*rho/pM)
    length_cylinder = 60e-2
    c = 343
    p = run_simulation(length_simulation, sample_rate, gamma, zeta, length_cylinder, c)

    tcalc = time.time() - t1
    print("Temps de calcul : " + str(tcalc) + "s")
    # play(p)

    # Scipy
    omega1 = 2 * np.pi * f1  # Conversion freq/puls
    omega2 = 2 * np.pi * f2
    F1 = 2 * c / length_cylinder  # Coef. premier mode
    F2 = 4 * c / length_cylinder  # Coef. premier mode

    A = zeta * (3 * gamma - 1) / 2 / np.sqrt(gamma)
    B = -zeta * (3 * gamma + 1) / 8 / gamma ** (3 / 2)
    C = -zeta * (gamma + 1) / 16 / gamma ** (5 / 2)
    model_args = (
        F1,
        F2,
        A,
        B,
        C,
        omega1,
        omega2,
    )  # Paramètres pour 2 modes

    def integrate_func(_, X):
        return state_function(X, model_args)

    y0 = np.array([gamma, 0.1, gamma, 0.1])  # Pour deux modes
    sol = integrate.solve_ivp(integrate_func, t_span=[0, length_simulation], y0=y0,
                              t_eval=np.linspace(0, length_simulation, int(length_simulation*sample_rate)))
    out_waveform = sol.y[0] + sol.y[2]
    normalized_waveform = out_waveform / max(np.abs(out_waveform))

    print("Scipy simulation done")
    sf.write("scipy_test.wav", out_waveform, sample_rate)
    sf.write("scipy_normalized.wav", normalized_waveform, sample_rate)
    # plt.plot(times, p, "orange", linewidth=2)
    # plt.plot(p)
    # plt.xlabel("time (s)")
    # plt.ylabel("pressure")
    # # plt.xlim(0, 0.5)
    # plt.ticklabel_format(style="sci", axis="x", scilimits=(0, 0))
    # # plt.ylim(0,0.000000000001)
    # plt.xlim()
    # plt.grid(True)

    # plt.figure()
    # plt.plot(sol.y)
    print("hey!")