fontSize = 14; 
%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
% MAPPING INITIAL - OSCILLATIONS ENTRETENUES 
%----------------------------------------------------------------------
num_samples = 30 %Nombre de points pour le mapping initiale
iterations =  100

modele = "modale" %modèle choisit : guide_onde ou modale
descriptor = "are_there_oscillations"  % Descripteur à observer
instrument ='saxophone'

abscisse = "gamma"
abscisse_max = 1
ordonnee = "zeta"
ordonnee_max =1

%Chargement des paramètres des modèles
t_max= 0.3 %durée de la simulation
Fe = 44100 %Fréquence d'échantillonnage
L= 0.6 %longueur du cylindre
c = 340 
nb_mode = 2
durete_rampe = 200
arg_modele= [t_max Fe L c nb_mode durete_rampe] 

%Chargement des paramètres des descripteurs
if descriptor == "are_there_oscillations"

    %++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    % MAPPING INITIAL - OSCILLATIONS ENTRETENUES 
    %----------------------------------------------------------------------
    dim1 = [0,abscisse_max] %étendue des axes, ici gamma
    dim2 = [0,ordonnee_max]%zeta
    epsilon = 0.1 %critère d'oscillations
    arg_descriptor= [epsilon]
    %-------------------------------------------------------------------------
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
                    instrument=instrument, ...
                    arg_modele=arg_modele, ...
                    arg_descriptor=arg_descriptor, ...
                    note_frequencies=note_frequencies)))

     %++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
     % MAPPING RAFFINÉ - OSCILLATIONS ENTRETENUES 
     %--------------------------------------------------------------------------
     %Calcul de sa SVM
     svm =CODES.fit.svm(X,label);
     for i=2:iterations
         %Calcul d'un nouveau sample
         x_mm=CODES.sampling.mm(svm,[min(dim1) min(dim2)],[max(dim1) max(dim2)]);
         %Calcul de son label
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

         label = [label;labels(end)]
         X=[X; x_mm]
         %Calcul de la SVM raffinée
         svm=CODES.fit.svm(X,label);
     end
     figure('Position',[200 200 500 500])
     svm.isoplot
     title("\bf Oscillations mapping pour le/la "+ instrument, 'FontSize', fontSize)
     xlabel('{\bf Gamma}', 'FontSize', fontSize)
     ylabel('{\bf Zeta}', 'FontSize', fontSize)
     save('X.mat','X')
     save('labels.mat','label')

elseif descriptor == "pitch"
    note_frequencies = [65.41, 69.3, 73.42, 77.78, 82.41, 87.31, 92.5, 98, 103.83, 110, 116.54, 123.47, 130.8] %fréquences harmoniques
    freq_ = [1 2 3 4 5 6 7 8 9 10 11 12 13] %Fréquences observées pour la classification one VS all
    zeta = 0.5 %zeta constant 
    epsilon_length = 0.05 
    osc_threshold = 0.15 % threshold to decide whether there are oscillations or not
    cents_threshold = 15 %marge 
    dim1 = [0.1,abscisse_max] %valeurs de gamma
    dim2 = [ c/(4*note_frequencies(end))-epsilon_length,  c/(4*note_frequencies(1))+epsilon_length]

    figure('Position',[200 200 500 500])

    for i=1:length(freq_)
        freq__ = freq_(i)
        %--------------------------------------------------------------------------
        % Sélection de points au hasard : 
        arg_descriptor= [Fe osc_threshold cents_threshold zeta freq__] 
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
                            instrument=instrument, ...
                            arg_modele=arg_modele, ...
                            arg_descriptor=arg_descriptor, ...
                            note_frequencies=note_frequencies)))

        for j=1:length(label)
            if label(j) ~=freq__               
                label(j)= 0
            end
        end

        if sum(label)==0 
            continue
        else 
            %++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            %++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            % MAPPING RAFFINÉ - OSCILLATIONS ENTRETENUES 
            %--------------------------------------------------------------------------
            %Calcul de sa SVM
            svm =CODES.fit.svm(X,label);
            for n=2:iterations
                %Calcul d'un nouveau sample
                x_mm=CODES.sampling.mm(svm,[min(dim1) min(dim2)],[max(dim1) max(dim2)]);
                %Calcul de son label
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

                label = [label;labels(end)]
                X=[X; x_mm]
                %Calcul de la SVM raffinée
                svm=CODES.fit.svm(X,label);    
            end
            hold on
            svm.isoplot
        end
    end

    %{
    freq0 = 0
    X  = double(pyrunfile("mapping_initialisation.py","X", ...
        abscisse=abscisse, ...
        ordonnee=ordonnee, ...
        dim1 =dim1, ...
        dim2=dim2, ...
        num_samples=num_samples))%Initialisation des points  
    arg_descriptor= [Fe osc_threshold cents_threshold zeta freq0] 
    %--------------------------------------------------------------------------
    %Initialisation des labels : 
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

    for j=1:length(label)
        if label(j) ~=0 
            label(j) =1
        end
    end

    if sum(label)~=length(label)
        svm =CODES.fit.svm(X,label);
        for i=2:80
        
            %Calcul d'un nouveau sample
            x_mm=CODES.sampling.mm(svm,[min(dim1) min(dim2)],[max(dim1) max(dim2)]);
            %Calcul de son label
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
        
             for j=1:length(labels)
                 if labels(j) ~=0 
                     labels(j)=1
                 end
             end                
             label = [label;labels(end)]
             X=[X; x_mm]
             %Calcul de la SVM
             svm=CODES.fit.svm(X,label);  
        end
        hold on
        svm.isoplot
    end
    %}

    title('{\bf Oscillations mapping pour }'+instrument, 'FontSize', fontSize)
    xlabel(abscisse, 'FontSize', fontSize)
    ylabel(ordonnee, 'FontSize', fontSize)
end

