% python -c "import sys; print(sys.executable)"
%pe = pyenv('Version', '/Users/fouilloumalena/opt/anaconda3/bin/python')

%--------------------------------------------------------------------
% Mapping oscillations entretenues ou non par méthode modale

% Échantillons dans l'espace
S=load("X_modale.mat");
X=deal(S.X);

% labels
S=load("labels_modale.mat");
label=transpose(deal(S.labels_modale));

%Calcul de la SVM
svm=CODES.fit.svm(X,label);
figure('Position',[200 200 500 500])
svm.isoplot

for i=2:50
    %Calcul d'un nouveau sample
    x_mm=CODES.sampling.mm(svm,[0 0],[1 1]);
    %Calcul de son label
    X_label = [X(end,:);x_mm];
    labels  = transpose(double(pyrunfile("modele_modale.py","labels",parameters = X_label)))
    label = [label;labels(end)]
    X=[X; x_mm]
    %Calcul de la SVM
    svm=CODES.fit.svm(X,label);    
end
hold on 
svm.isoplot
title("Absence ou présence d'oscillations entretenues")
xlabel("gamma")
ylabel("zeta")
legend('Before','After optimization','-1 samples','+ 1samples')
