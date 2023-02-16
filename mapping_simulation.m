fontSize = 14; 
%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
% By Malena Fouillou
%
% Implémentation de la méthode d'échantillonnage adaptatif dans le cas d'une étude des régimes
% de fonctionnement des instruments auto-oscillant : clarinette et violon.
%
% --> Elle comprend en entrée la définiton des paramètres observée souhaités : 
%     - le type d'instrument : clarinette,violon
%     - le descripteur : soit le pitch , soit la présence de son 
%     - le type de modèle pour la simulation : guide d'onde ou modale
%     - les paramètres de contrôle observés : gamma/zeta ou
%       gamma/longueur du résonnateur
%     - 
%
% --> L'algorithme fait appel à des fonctions Python situés dans 'run_simulation.py, 'descripteurs_utiles.py' et dans le dossier
%     "modelisation_physique".
%
%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

instrument ='clarinette'                                                   % Type d'instrument étudié
descriptor = "are_there_oscillations"                                      % Descripteur à observer
modele = "modale"                                                      % Modèle choisit 


% Paramètres de contrôle 
abscisse = "gamma" 
abscisse_max = 1                                                           %Étendue de l'axe
ordonnee = "zeta" 
ordonnee_max = 2

% Chargement des paramètres des modèles
t_max= 0.3                                                                 % Durée de la simulation (secondes)
Fe = 44100                                                                 % Fréquence d'échantillonnage (Hz)
L= 0.6                                                                    % Longueur du cylindre/corde (mètre)
c = 340                                                                    % Vitesse des ondes dans l'instrument
nb_mode = 2                                                                % Nombre de modes considérés ( dans la méthode modale )
durete_rampe = 20                                                          % Pente d'évolution de gamma
% Arguments en entrée de la fonction du modèle considéré : 
arg_modele= [t_max Fe L c nb_mode durete_rampe] 

% Chargement des paramètres des descripteurs : fréquences harmoniques observées sur une gamme choisie
note_frequencies = [65.41, 69.3, 73.42, 77.78, 82.41, 87.31, 92.5, 98, 103.83, 110, 116.54, 123.47, 130.8] 

% Chargement des paramètres de sampling
num_samples = 30                                                           % Nombre de points pour le mapping initiale
iterations =  150                                                          % Nombre d'itérations de la méthode d'échantillonnage adaptatif

if descriptor == "are_there_oscillations"

    %++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    % ECHANTILLONNAGE INITIAL - OSCILLATIONS ENTRETENUES 
    %++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    % Paramètres descripteurs
    dim1 = [0.1,abscisse_max]                                              % Étendue des axes, ici gamma 
    dim2 = [0,ordonnee_max]                                                % Ici Zeta
    epsilon = 0.6                                                          % Critère d'amplitude d'oscillations 
    arg_descriptor= [epsilon]
    
    % Sélection de points au hasard : 
    X  = double(pyrunfile("mapping_initialisation.py","X", ...
                abscisse=abscisse, ...
                ordonnee=ordonnee, ...
                dim1 =dim1, ...
                dim2=dim2, ...
                num_samples=num_samples))
    
    % Initialisation des labels : 
    label = transpose(double(pyrunfile("run_simulation.py","y", ...
                    X=X, ...
                    descriptor=descriptor, ...
                    abscisse=abscisse, ...
                    ordonnee=ordonnee, ...
                    modele =modele, ...
                    instrument=instrument, ...
                    arg_modele=arg_modele, ...
                    arg_descriptor=arg_descriptor, ...
                    note_frequencies=note_frequencies)))

     
     % Calcul de sa SVM
     svm =CODES.fit.svm(X,label);
   
     %+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
     % ECHANTILLONNAGE ADAPTATIF - OSCILLATIONS ENTRETENUES 
     %+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
     for i=2:iterations
         % Calcul d'un nouveau sample
         x_mm=CODES.sampling.mm(svm,[min(dim1) min(dim2)],[max(dim1) max(dim2)]);
         % Calcul de son label
         X_label = [X(end,:);x_mm];
         labels = transpose(double(pyrunfile("run_simulation.py","y", ...
                             X=X_label, ...
                             descriptor=descriptor, ...
                             abscisse=abscisse, ...
                             ordonnee=ordonnee, ...
                             modele =modele, ...
                             instrument=instrument, ...
                             arg_modele=arg_modele, ...
                             arg_descriptor=arg_descriptor, ...
                             note_frequencies=note_frequencies)))
         % Ajout du nouvel échantillon au mapping
         label = [label;labels(end)]
         X=[X; x_mm]
         % Calcul de la SVM raffinée
         svm=CODES.fit.svm(X,label);
     end
     
     figure('Position',[200 200 500 500])
     svm.isoplot
     % title("\bf Oscillations mapping pour le/la "+ instrument, 'FontSize', fontSize)
     xlabel('{\bf \gamma}', 'FontSize', fontSize)
     ylabel('{\bf \zeta}', 'FontSize', fontSize)
     fontsize(gca, 12,'points') 
     legend('Location','northeast','NumColumns',2, 'Interpreter','latex')
     save('X.mat','X')
     save('labels.mat','label')



elseif descriptor == "pitch"
    
    %++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    % ECHANTILLONNAGE INITIAL : PITCH
    %++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    indices_freq_ = [8]                                                   % Fréquences observées pour la classification one VS all
    zeta = 0.6                                                             % Zeta constant 
    epsilon_length = 0.05                                                  % Marge de longueurde l'instrument
    osc_threshold = 0.6                                                    % Critère d'oscillations (ou non)
    cents_threshold = 15                                                   % Différence maximale en cent par rapport à la note de référence 
    dim1 = [0.1,abscisse_max]                                              % Valeurs de gamma
    dim2 = [ c/(4*note_frequencies(end))-epsilon_length,  c/(4*note_frequencies(1))+epsilon_length]

    figure('Position',[200 200 500 500])
    
    % Boucle sur chaque fréquence observée de la gamme harmonique
    for i=1:length(indices_freq_)

        freq__ = indices_freq_(i)
       
        % Sélection de points au hasard : 
        arg_descriptor= [Fe osc_threshold cents_threshold zeta ] 
        X  = double(pyrunfile("mapping_initialisation.py","X", ...
                    abscisse=abscisse, ...
                    ordonnee=ordonnee, ...
                    dim1 =dim1, ...
                    dim2=dim2, ...
                    num_samples=num_samples))%Initialisation des points
        
        % Initialisation des labels : 
        label = transpose(double(pyrunfile("run_simulation.py","y", ...
                            X=X, ...
                            descriptor=descriptor, ...
                            abscisse=abscisse, ...
                            ordonnee=ordonnee, ...
                            modele =modele, ...
                            instrument=instrument, ...
                            arg_modele=arg_modele, ...
                            arg_descriptor=arg_descriptor, ...
                            note_frequencies=note_frequencies)))
        
        for j=1:length(label) % Calcul des labels de la forme one VS all
            if label(j) ~=freq__               
                label(j)= 0
            end
        end

        if sum(label)==0                                                   % Si la fréquence observée n'est pas trouvé
                                                                           % (tous les labels       =0), l'algorithme passe
                                                                           % à la suivante, sinon il suit à la méthode
                                                                           % d'échantillonnage adaptatif
            continue
        else 

            % Calcul de sa SVM
            svm =CODES.fit.svm(X,label);

            %++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            % ECHANTILLONNAGE ADAPTATIF : PITCH
            %++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            for n=2:iterations
                % Calcul d'un nouveau sample
                x_mm=CODES.sampling.mm(svm,[min(dim1) min(dim2)],[max(dim1) max(dim2)]);
                % Calcul de son label
                X_label = [X(end,:);x_mm];
                labels = transpose(double(pyrunfile("run_simulation.py","y", ...
                                    X=X_label, ...
                                    descriptor=descriptor, ...
                                    abscisse=abscisse, ...
                                    ordonnee=ordonnee, ...
                                    modele =modele, ...
                                    instrument=instrument, ...
                                    arg_modele=arg_modele, ...
                                    arg_descriptor=arg_descriptor, ...
                                    note_frequencies=note_frequencies)))
    
                for j=1:length(label)
                   if label(j) ~=freq__    
                        label(j)= 0
                   end
                end  
                % Ajout du nouvel échantillon au mapping
                label = [label;labels(end)]
                X=[X; x_mm]
                %Calcul de la SVM raffinée
                svm=CODES.fit.svm(X,label);    
            end
            
            hold on
            svm.isoplot
            save('X_11.mat','X')
            save('labels_11.mat','label')
        end
        
    end

    %{
    % Cas particulier de la première fréquence observée (
    % note_frequencies(1))
    % telle que la fonction labels de 'run_simulation.py' renvoie idx = 0.
    freq0 = 0 
    %++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    % ECHANTILLONNAGE INITIAL : PITCH
    %++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    % Sélection de points au hasard : 
    X  = double(pyrunfile("mapping_initialisation.py","X", ...
        abscisse=abscisse, ...
        ordonnee=ordonnee, ...
        dim1 =dim1, ...
        dim2=dim2, ...
        num_samples=num_samples))%Initialisation des points  
    arg_descriptor= [Fe osc_threshold cents_threshold zeta] 
    
    % Initialisation des labels : 
    label = transpose(double(pyrunfile("run_simulation.py","y", ...
                      X=X, ...
                      descriptor=descriptor, ...
                      abscisse=abscisse, ...
                      ordonnee=ordonnee, ...
                      modele =modele, ...
                      instrument=instrument, ...
                      arg_modele=arg_modele, ...
                      arg_descriptor=arg_descriptor, ...
                      note_frequencies=note_frequencies)))

    for j=1:length(label) % Calcul des labels sous la forme  one VS all
        if label(j) ~=freq0 
            label(j) =1
        end
    end

    % Calcul de sa SVM
    svm =CODES.fit.svm(X,label);

    %++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    % ECHANTILLONNAGE ADAPTATIF : PITCH
    %++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    for i=2:iterations

        % Calcul d'un nouveau sample
        x_mm=CODES.sampling.mm(svm,[min(dim1) min(dim2)],[max(dim1) max(dim2)]);
        % Calcul de son label
        X_label = [X(end,:);x_mm];
        labels = transpose(double(pyrunfile("run_simulation.py","y", ...
                                 X=X_label, ...
                                 descriptor=descriptor, ...
                                 abscisse=abscisse, ...
                                 ordonnee=ordonnee, ...
                                 modele =modele, ...
                                 instrument=instrument, ...
                                 arg_modele=arg_modele, ...
                                 arg_descriptor=arg_descriptor, ...
                                 note_frequencies=note_frequencies)))
        
         for j=1:length(labels) % Calcul des labels pour obtenir le cas one VS
         %all 
             if labels(j) ~=freq0
                 label(j) =1
             end
         end 
         % Ajout du nouvel échantillon au mapping
         label = [label;labels(end)]
         X=[X; x_mm]
         % Calcul de la SVM raffinée
         svm=CODES.fit.svm(X,label);  
     end
     
    hold on
    svm.isoplot
    save('X_0.mat','X')
    save('labels_0.mat','label')
    
    xlabel(abscisse, 'FontSize', fontSize)
    ylabel(ordonnee, 'FontSize', fontSize)
    %}
end

