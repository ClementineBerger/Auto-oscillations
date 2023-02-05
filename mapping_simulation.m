%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
% MAPPING INITIAL - OSCILLATIONS ENTRETENUES 
%----------------------------------------------------------------------
num_samples = 100 %Nombre de points pour le mapping initiale
abscisse = 'gamma' 
ordonnee = 'lenght_cylinder'
modele = "guide_onde" %modèle choisit : guide_onde ou modale
descriptor = "are_there_oscillations"  % Descripteur à observer

%Chargement des paramètres des modèles
t_max= 0.3 %durée de la simulation
Fe = 44100 %Fréquence d'échantillonnage
L= 0.6 %longueur du cylindre
c = 340  %célérité
note_frequencies = [65.41 69.3 73.42 77.78 82.41 87.31 92.5 98 103.83 110 116.54 123.47] %fréquences harmoniques
nb_mode = 1

arg_modele= [t_max Fe L c nb_mode] 

%Chargement des paramètres des descripteurs
if descriptor == "are_there_oscillations"
    dim1 = [0,1] %étendue des axes, ici gamma
    dim2 = [0,1]%zeta
    epsilon = 0.1 %critère d'oscillations
    arg_descriptor= [epsilon]

elseif descriptor == "pitch"
    freq = 8 %Fréquence observée pour la classification one VS all
    zeta = 0.5 %zeta constant 
    epsilon_length = 0.05 
    osc_threshold = 0.15 % threshold to decide whether there are oscillations or not
    cents_threshold = 15 %marge 
    dim1 = [0,1] %valeurs de gamma
    dim2 = [ c/(4*note_frequencies(end))-epsilon_length,  c/(4*note_frequencies(1))+epsilon_length]
    disp(dim2)
    arg_descriptor= [Fe osc_threshold cents_threshold zeta freq]   
end

%--------------------------------------------------------------------------
% Sélection de points au hasard : 
X  = double(pyrunfile("mapping_initialisation.py","X", ...
    abscisse=abscisse, ...
    ordonnee=ordonnee, ...
    dim1 =dim1, ...
    dim2=dim2, ...
    num_samples=num_samples))%Initialisation des points
%--------------------------------------------------------------------------
%Initialisation des labels : 
label = transpose(double(pyrunfile("run_simulation.py","y", ...
                X=X, ...
                descriptor=descriptor, ...
                abscisse=abscisse, ...
                ordonnee=ordonnee, ...
                modele =modele, ...
                arg_modele=arg_modele, ...
                arg_descriptor=arg_descriptor, ...
                note_frequencies=note_frequencies)))
%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
% MAPPING RAFFINÉ - OSCILLATIONS ENTRETENUES 
%--------------------------------------------------------------------------
%Calcul de sa SVM
svm_8 =CODES.fit.svm(X,label);

for i=2:80
    %Calcul d'un nouveau sample
    x_mm=CODES.sampling.mm(svm_8,[min(dim1) min(dim2)],[max(dim1) max(dim2)]);
    %Calcul de son label
    X_label = [X(end,:);x_mm];
    labels = transpose(double(pyrunfile("run_simulation.py","y", ...
                X=X_label, ...
                descriptor=descriptor, ...
                abscisse=abscisse, ...
                ordonnee=ordonnee, ...
                modele =modele, ...
                arg_modele=arg_modele, ...
                arg_descriptor=arg_descriptor, ...
                note_frequencies=note_frequencies)))
    label = [label;labels(end)]
    X=[X; x_mm]
    %Calcul de la SVM
    svm_8=CODES.fit.svm(X,label);    
end
figure('Position',[200 200 500 500])
svm_8.isoplot