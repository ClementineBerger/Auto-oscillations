%--------------------------------------------------------------------
% Mapping oscillations entretenues ou non par méthode guide d'onde

% Échantillons dans l'espace
S=load("X_guide_onde.mat");
X=deal(S.X);

% labels
S=load("labels_guide_onde.mat");
label=transpose(deal(S.labels_guide_onde));

%Calcul de la SVM
svm=CODES.fit.svm(X,label);
figure('Position',[200 200 500 500])
%svm.isoplot


for i=2:80
    %Calcul d'un nouveau sample
    x_mm=CODES.sampling.mm(svm,[0 0],[1 1]);
    %Calcul de son label
    X_label = [X(end,:);x_mm];
    labels  = transpose(double(pyrunfile("guide_d_onde.py","labels",parameters = X_label)))
    label = [label;labels(end)]
    X=[X; x_mm]
    %Calcul de la SVM
    svm=CODES.fit.svm(X,label);    
end
hold on 
svm.isoplot
%--------------------------------------------------------------------