"""
@author : Clémentine BERGER & Amélie PICARD

Implémentation guide d'onde suivant l'article de McIntyre : à l'avantage d'être plus modulable
avec la possibilité de changer de fonction de réflexion au bout du guide d'onde

Ce script fonctionne pour une simulation de longueur L et pour une corde pincée en son MILIEU
"""


### Importation des bibliothèques

import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as sig
import scipy.integrate as intgr

### Paramètres utilisateurs

# c = célérité des ondes sonores
# L = longueur du guide d'onde
# gamma = rapport pression de bouche / pression de plaquage
# zeta = paramètre caractéristique de l'anche
# type_reflection = dirac ou triangle (essayer de rajouter gaussien)
# frac_T = pour le type triangle -> défini la demi largeur du triangle égale à T/frac_T


### Définition des fonctions


def retardT(l, c0):
    """
    Renvoie T le retard accumulé par l'onde
    en un aller-retour
    l : longueur du guide cylindrique
    c0 : célérité des ondes dans l'air
    """
    return 2 * l / c0


def coeffs(gamma, zeta):
    """Calcule les coefficients de la fonction de
    couplage F linéarisée
    F(p) = F0 + Ap + Bp**2 + Cp**3
    """
    if gamma == 0:
        return 0, 0, 0, 0
    else:
        F0 = zeta * (1 - gamma) * np.sqrt(gamma)
        A = zeta * (3 * gamma - 1) / 2 / np.sqrt(gamma)
        B = -zeta * (3 * gamma + 1) / 8 / gamma ** (3 / 2)
        C = -zeta * (gamma + 1) / 16 / gamma ** (5 / 2)
    return F0, A, B, C


def Fclarinette(list_p, gamma, zeta):
    """
    Renvoit le débit u suivant la pression p
    suivant la relation u = F(p)
    """
    if gamma == 0:
        return np.zeros(len(list_p))
    else:
        valid = (gamma - list_p < 1) & (gamma - list_p > 0)
        sgn = (gamma - list_p) / np.abs(gamma - list_p)
        # u = zeta * (1 - gamma + list_p) * np.nan_to_num(np.sqrt(gamma - list_p)) * valid
        u = zeta * (1 - gamma + list_p) * np.sqrt(np.abs(gamma - list_p)) * valid * sgn
    return u


def tableau_Fsimulation(pmin, pmax, nb_pts, gamma, zeta):
    """
    Rempli un tableau F pour faire la recherche de 0

    pmin = borne inférieure de p
    pmax = borne supérieure de p
    nb_pts = nombre de points de calculs
    gamma =
    zeta =
    """
    tab_p = np.linspace(pmin, pmax, nb_pts)
    tab_F = Fclarinette(tab_p, gamma, zeta)

    return tab_p, tab_F


def find_zero(tableau, i):
    """
    Recherche le point d'annulation de tableau le plus proche possible de i

    tableau = tableau des valeurs de la fonction F sur l'intervalle souhaité
    i =
    """
    taille = len(tableau)
    changement_signe = (
        tableau[0 : taille - 1] * tableau[1:taille]
    )  # il y a un point d'annulation entre tableau[j] et tableau[j+1] ssi tableau[j]*tableau[j+1] <= 0
    negatif = changement_signe <= 0  # True aux indices où il y a un changement de signe
    tab_i0 = (np.arange(taille - 1))[
        negatif
    ]  # indices auxquels il y a un changement de signe
    if len(tab_i0) == 0:
        return np.argmin(np.abs(tableau))
    i0 = np.argmin(
        np.abs(tab_i0 - i)
    )  # indice de l'indice le plus proche de i dans tab_i0
    return tab_i0[i0]


def convolution(ind_tau, reflex_list, signal_list):
    """
    Calcul de la convolution entre le signal p + u et la fonction de réflexion
    (aux temps passés) avec une intégration par la méthode des trapèzes

    ind_tau = indice du temps de calcul courant
    reflex_list = liste des coefficients de réflexion dans le temps
    signal_list = liste p + u

    (plus rapide que scipy...)
    """

    x1 = reflex_list[0 : ind_tau + 1]
    x2 = np.flipud(signal_list[0 : ind_tau + 1])

    integrate = intgr.trapz(
        y=x1[0 : min(len(x1), len(x2)) - 1] * x2[0 : min(len(x1), len(x2)) - 1]
    )
    # integrate = intgr.trapz(reflex_list*np.flipud(signal_list))

    return integrate


def convolution_triangle(ind_tau, T, fe, frac_T, reflex_list, signal_list):
    """
    Calcul de la convolution entre le signal p + u et la fonction de réflexion
    (aux temps passés) avec une intégration par la méthode des trapèzes

    ind_tau = indice du temps de calcul courant
    reflex_list = liste des coefficients de réflexion dans le temps
    signal_list = liste p + u

    (plus rapide que scipy...)
    """

    indT = int(T * fe)

    delta_ind = indT // frac_T

    if ind_tau <= indT - delta_ind:
        return 0

    elif ind_tau <= indT + delta_ind:
        x1 = reflex_list[indT - delta_ind : ind_tau + 1]
        x2 = np.flipud(signal_list[0 : ind_tau - (indT - delta_ind) + 1])

    else:
        x1 = reflex_list[indT - delta_ind : indT + delta_ind + 1]
        x2 = np.flipud(
            signal_list[ind_tau - (indT + delta_ind) : ind_tau - (indT - delta_ind) + 1]
        )

    integrate = intgr.trapz(y=x1 * x2)

    return integrate


def reflexion(T, pertes_dirac, frac_T, rate_gauss, fe, Nsim, type):
    """
    Calcule la liste des coefficients de réflexion pour plusieurs formes de fonction de réflexion

    type = str donnant le type de réflexion choisi ; 'dirac', 'triangle'
    (si possible 'exponentiel' mais nécessite de revoir un peu le code...)
        - dirac : r(t) = -delta(t-T)
        - triangle : triangle négatif centré en T (plus il est court, plus on se rapproche du dirac et des créneaux)
        - gaussienne : -a*exp(-b(t-T)**2)
    """

    indT = int(T * fe)  # indice du moment T de la réflexion au bout du guide

    if type == "dirac":
        reflex_list = np.zeros(Nsim)
        reflex_list[indT] = -pertes_dirac

    elif type == "triangle":  # centré en T
        reflex_list = np.zeros(Nsim)
        delta_ind = indT // frac_T
        pente = 1 / delta_ind

        for i in range(indT - delta_ind, indT + 1):
            reflex_list[i] = (i - indT + delta_ind) * pente

        for i in range(indT + 1, indT + delta_ind + 1):
            reflex_list[i] = reflex_list[indT] - (i - indT) * pente

        aire = np.sum(reflex_list)
        # aire = intgr.trapz(y=reflex_list,dx=1/fe)
        # aire = np.max(abs(reflex_list))

        reflex_list = -reflex_list / aire

    elif type == "gauss":
        demi_largeur = rate_gauss * T
        sigma = demi_largeur / np.sqrt(2 * np.log(2))
        b = 1 / (2 * (sigma ** 2))
        a = 1 / (
            sigma * np.sqrt(2 * np.pi)
        )  ### à revoir, le fait que l'aire de r doit être égale à 1
        tps = np.linspace(0, Nsim / fe, Nsim)
        reflex_list = -np.exp(-b * ((tps - T) ** 2))
        # aire = intgr.trapz(y=reflex_list,dx=1/fe)
        # aire = np.max(abs(reflex_list))
        aire = np.sum(abs(reflex_list))
        reflex_list /= abs(aire)

    return reflex_list


def calcul_rampe(t_rampe, gamma, sample_rate, time):
    gammas = gamma * np.ones(len(time))
    pente = gamma / t_rampe
    gammas[0 : int(t_rampe * sample_rate) + 1] = (
        pente * time[0 : int(t_rampe * sample_rate) + 1]
    )
    return gammas


def clarinette(
    t_max,
    sample_rate,
    gamma,
    zeta,
    type_reflection,
    l,
    c0,
    rampe=False,
    t_rampe=0.2,
    pertes_dirac=1,
    frac_T=10,
    rate_gauss=0.1,
    fig=False,
    sound=False,
):
    """
    Renvoit la pression p et le débit u (adimensionnés) simulés avec
    les paramètres gamma, zeta :

    t_max : durée de la simulation en s
    fe : fréquence d'échantillonnage de la simulation en Hz
    gamma : contrôle de la pression de bouche
    zeta : contrôle anche
    type_reflection : type de réflexion au bout du guide, 'dirac', 'triangle' ou 'gauss'
    frac_T : seulement pour le type 'triangle', définition de la demi-largeur du triangle T/frac_T
    rate_gauss : demi-largeur à mi-hauteur (typiquement entre 0.05 et 0.4)
    l : longueur du cylindre
    c0 : célérité des ondes
    """

    # Initialisation des paramètres
    T = retardT(l, c0)
    indT = int(T * sample_rate)

    # F0, A, B, C = coeffs(gamma, zeta)

    time = np.arange(int(t_max * sample_rate)) / sample_rate  # temps de simulation
    Nsim = len(time)

    p = np.zeros(Nsim)
    u = np.zeros(Nsim)

    reflex_list = reflexion(
        T, pertes_dirac, frac_T, rate_gauss, sample_rate, Nsim, type=type_reflection
    )

    ######## SIMULATION

    tab_p, tab_F = tableau_Fsimulation(
        -5, 5, 2000, gamma, zeta
    )  # changer ça pour pouvoir rajouter une rampe ....
    solvF = tab_p - tab_F

    if rampe:
        gammas = calcul_rampe(t_rampe, gamma, sample_rate, time)
        ind_rampe = int(t_rampe * sample_rate)
        tabs_p = np.zeros((ind_rampe, len(tab_p)))
        tabs_F = np.zeros((ind_rampe, len(tab_F)))
        for i in range(ind_rampe):
            tabs_p[i, :], tabs_F[i, :] = tableau_Fsimulation(
                -5, 5, 2000, gammas[i], zeta
            )
        solvFs = tabs_p - tabs_F
    else:
        gammas = gamma * np.ones(Nsim)

    i_act = np.argmin(np.abs(tab_p - gamma)) + 1

    if type_reflection == "dirac":
        for j in range(Nsim):
            if j < indT:
                ph = 0
            elif rampe and j < ind_rampe:
                ph = -(p[j - indT] + u[j - indT])
                i = find_zero(solvFs[j] - ph, i_act)
                i_act = i
                p[j] = tabs_p[j, i]
                u[j] = tabs_F[j, i]
            else:
                ph = -(p[j - indT] + u[j - indT])
                i = find_zero(solvF - ph, i_act)
                i_act = i
                p[j] = tab_p[i]
                u[j] = tab_F[i]

    elif type_reflection == "triangle":
        for j in range(Nsim):
            ph = convolution_triangle(
                ind_tau=j,
                T=T,
                fe=sample_rate,
                frac_T=frac_T,
                reflex_list=reflex_list,
                signal_list=p + u,
            )
            # ph = convolution(ind_tau=j,reflex_list = reflex_list, signal_list = p + u)
            if rampe and j < ind_rampe:
                i = find_zero(solvFs[j] - ph, i_act)
                i_act = i
                p[j] = tab_p[i]
                u[j] = tab_F[i]
            else:
                i = find_zero(solvF - ph, i_act)
                i_act = i
                p[j] = tab_p[i]
                u[j] = tab_F[i]

    elif type_reflection == "gauss":
        for j in range(Nsim):
            ph = convolution(ind_tau=j, reflex_list=reflex_list, signal_list=p + u)
            # print(ph)
            if rampe and j < ind_rampe:
                i = find_zero(solvFs[j] - ph, i_act)
                i_act = i
                p[j] = tab_p[i]
                u[j] = tab_F[i]
            else:
                i = find_zero(solvF - ph, i_act)
                i_act = i
                p[j] = tab_p[i]
                u[j] = tab_F[i]
    if fig:
        plt.figure(figsize=(10, 5))
        plt.plot(time, p)
        plt.xlim(0, 0.2)
        plt.ylim(-1.1, 1.1)
        plt.tight_layout()
        plt.xlabel("Temps en s", size=14)
        plt.ylabel("Amplitude", size=14)
        plt.show()

    return p, u


####### Instruments à cordes frottées


def Fcordes(v, vb, v0, Fb, mu_s, mu_d):
    dv = (vb - v) / v0
    # dv = v/v0
    a = 2 * (mu_s - mu_d) * Fb
    b = mu_d * Fb
    sgn = (dv) / abs(dv)
    return a * dv / (1 + dv ** 2) + b


def tableau_Fcordes(vmin, vmax, nb_pts, vb, v0, Fb, mu_s, mu_d):
    """
    Rempli un tableau F pour faire la recherche de 0

    vmin = borne inférieure de v
    vmax = borne supérieure de v
    nb_pts = nombre de points de calculs
    """
    tab_v = np.linspace(vmin, vmax, nb_pts)
    tab_f = Fcordes(tab_v, vb, v0, Fb, mu_s, mu_d)

    return tab_v, tab_f


def reflexion_cordes(alpha1, alpha2, max_ref, Nsim, sample_rate, beta, l, c0):
    """ Génération de la fonction de réflexion globale (sur le chevalet
    et sur le sillet)

    Args:
        alpha1 (_float_): coefficient de réflexion au chevalet
        alpha2 (_float_): coefficient de réflexion au sillet
        max_ref (_int_): nombre de réflexions max considérées de part et d'autre
        Nsim (_int_): nombre d'échantillons temporels
        sample_rate (_int_): fréquence d'échantillonnage
        beta (_float_): portion de la longueur de la corde où se trouve l'archet
        l (_float_): longueur de la corde
        c0 (_float_): célérité des ondes transversales

    Returns:
        _array_: vecteur contenant la fonction de réflexion
    """
    alpha1 = -0.49
    alpha2 = -0.49

    r_idea = np.zeros(Nsim)
    ref = 1
    eps = 1e-4

    max_ref = 15

    nb_alphas1 = np.zeros(2 * max_ref)
    nb_alphas1[0::2] = np.arange(1, max_ref + 1)
    nb_alphas1[1::2] = np.arange(1, max_ref + 1)
    print(nb_alphas1)

    nb_alphas2 = np.zeros(2 * max_ref)
    nb_alphas2[1:] = nb_alphas1[:-1]
    print(nb_alphas2)

    distances = 2 * beta * l + nb_alphas1 + 2 * (1 - beta) * l + nb_alphas2
    ind_tps = (sample_rate * distances / c0).astype(int)
    coeffs_ref = (alpha1 ** nb_alphas1) * (alpha2 ** nb_alphas2)

    r_idea[ind_tps] += coeffs_ref

    distances = 2 * (1 - beta) * l + nb_alphas1 + 2 * (beta) * l + nb_alphas2
    ind_tps = (sample_rate * distances / c0).astype(int)
    coeffs_ref = (alpha1 ** nb_alphas1) * (alpha2 ** nb_alphas2)

    r_idea[ind_tps] = coeffs_ref

    return r_idea


def find_zero_cordes(tableau, iprevious):
    """
    Recherche le point d'annulation de tableau le plus proche possible de i

    tableau = tableau des valeurs de la fonction F sur l'intervalle souhaité
    iprevious = indice du précédent 0
    """

    indmin = np.argmax(tableau)
    indmax = np.argmin(tableau)

    taille = len(tableau)
    changement_signe = (
        tableau[0 : taille - 1] * tableau[1:taille]
    )  # il y a un point d'annulation entre tableau[j] et tableau[j+1] ssi tableau[j]*tableau[j+1] <= 0
    negatif = changement_signe <= 0  # True aux indices où il y a un changement de signe
    tab_i0 = (np.arange(taille - 1))[
        negatif
    ]  # indices auxquels il y a un changement de signe
    if len(tab_i0) == 0:
        return np.argmin(np.abs(tableau))
    if iprevious in np.arange(indmin, indmax + 1):
        for i in tab_i0:
            if i in np.arange(indmin, indmax):
                return tab_i0[i]
    else:
        i0 = np.argmin(
            np.abs(tab_i0 - iprevious)
        )  # indice de l'indice le plus proche de iprevious dans tab_i0
    return tab_i0[i0]


def cordes(
    t_max,
    sample_rate,
    gamma,
    zeta,
    beta,
    l,
    type_reflection="dirac",
    rampe=False,
    t_rampe=0.2,
    pertes_dirac=1,
    frac_T=10,
    rate_gauss=0.1,
    fig=False,
    sound=False,
):
    """Simulation du violon par la méthode du guide d'onde

    Args:
        t_max (_float_): durée de la simulation en s
        sample_rate (_type_): fréquence d'échantillonnage en Hz
        gamma (_type_): vb vitesse de l'archet sur la corde
        zeta (_type_): force exercée par l'archet sur la corde
        beta (_type_): fraction de la longueur de la corde correspondant à la position de l'archet
        l (_type_): longeur de la corde
        type_reflection (str, optional): inutile dans ce modèle. Defaults to 'dirac'.
        rampe (bool, optional): pour l'instant inutile, je vais essayer de le rajouter. Defaults to False.
        t_rampe (float, optional): _description_. Defaults to 0.2.
        pertes_dirac (int, optional): _description_. Defaults to 1.
        frac_T (int, optional): _description_. Defaults to 10.
        rate_gauss (float, optional): _description_. Defaults to 0.1.
        fig (bool, optional): _description_. Defaults to False.
        sound (bool, optional): _description_. Defaults to False.
    """

    vb = gamma
    Fb = zeta

    v0 = 0.008  # paramètre de régularisation pour la fonction non-linéaire

    Nsim = int(t_max * sample_rate)

    tps = np.linspace(0, Nsim / sample_rate, Nsim)

    rho = 3.1e-3
    T = 51.9
    Z = np.sqrt(T * rho)

    c0 = np.sqrt(T / rho)

    fond = c0 / 2 / l

    # Z = 1/2

    mu_s = 0.4
    mu_d = 0.2

    alpha1 = -0.5
    alpha2 = -0.49
    max_ref = 15

    v = np.zeros(Nsim)
    v[0] = vb

    f = np.zeros(Nsim)
    f[0] = Fb

    per = 2 * l / c0
    tadh = (1 - beta) * per
    tgliss = beta * per

    ind_adh = int(tadh * sample_rate)
    indT = int(per * sample_rate)
    ind_gliss = indT - ind_adh

    reflex_list = reflexion_cordes(
        alpha1, alpha2, max_ref, Nsim, sample_rate, beta, l, c0
    )

    tab_v, tab_f = tableau_Fcordes(
        -vb * (1 - beta) / beta - 0.5,
        2 * vb * (1 - beta) / beta + 0.5,
        4000,
        vb,
        v0,
        Fb,
        mu_s,
        mu_d,
    )

    solvF = tab_v - tab_f / 2 / Z
    plt.plot(tab_v, tab_f / 2 / Z, color="darkblue")

    iprevious = np.argmin(tab_f) - 10
    vhs = []

    for j in range(Nsim):
        vh = convolution(ind_tau=j, reflex_list=reflex_list, signal_list=v + f / 2 / Z)
        i = find_zero(solvF - vh, iprevious)
        iprevious = i
        vhs.append(vh)
        v[j] = tab_v[i]
        f[j] = tab_f[i]

    if fig:
        plt.figure(figsize=(10, 5))
        plt.plot(tps, v)
        plt.xlim(0, 0.2)
        plt.ylim(-1.1, 1.1)
        plt.tight_layout()
        plt.xlabel("Temps en s", size=14)
        plt.ylabel("Amplitude", size=14)
        plt.show()

    return v, f


def guide_onde(
    instrument,
    t_max,
    sample_rate,
    gamma,
    zeta,
    l,
    c0=340,
    beta=0.3,
    type_reflection="dirac",
    rampe=False,
    t_rampe=0.2,
    pertes_dirac=1,
    frac_T=10,
    rate_gauss=0.1,
    fig=False,
    sound=False,
):

    if instrument == "clarinette":
        return clarinette(
            t_max=t_max,
            sample_rate=sample_rate,
            gamma=gamma,
            zeta=zeta,
            type_reflection=type_reflection,
            l=l,
            c0=c0,
            rampe=rampe,
            t_rampe=t_rampe,
            pertes_dirac=pertes_dirac,
            frac_T=frac_T,
            rate_gauss=rate_gauss,
            fig=fig,
        )

    if instrument == "corde":
        return cordes(
            t_max=t_max,
            sample_rate=sample_rate,
            gamma=gamma,
            zeta=zeta,
            beta=beta,
            l=l,
            fig=fig,
        )
    else:
        print("Mauvais nom d'instrument : 'clarinette' ou 'corde' ")
        return 0
