%python -c "import sys; print(sys.executable)"
%pe = pyenv('Version', '/Users/fouilloumalena/opt/anaconda3/bin/python')
%--------------------------------------------------------------------
% Mapping avec pitch 0


% Échantillons dans l'espace
S=load("X_pitch_0.mat");
X=deal(S.X);

% Paramètres 
length_min  = pyrunfile("pitch_mapping.py","length_min",parameters = X)
length_max  = pyrunfile("pitch_mapping.py","length_max",parameters = X)

% labels
S=load("labels_pitch_0.mat");
label=transpose(deal(S.labels_pitch_0));

%Calcul de la SVM
svm_0=CODES.fit.svm(X,label);
figure('Position',[200 200 500 500])
%svm.isoplot

for i=2:80
    %Calcul d'un nouveau sample
    x_mm=CODES.sampling.mm(svm_0,[0 length_min],[1 length_max]);
    %Calcul de son label
    X_label = [X(end,:);x_mm];
    labels  = transpose(double(pyrunfile("pitch_mapping.py","labels",parameters = X_label)))
    label = [label;labels(end)]
    X=[X; x_mm]
    %Calcul de la SVM
    svm_0=CODES.fit.svm(X,label);    
end

hold on 
svm_0.isoplot

%--------------------------------------------------------------------
% Mapping avec pitch 1
% Échantillons dans l'espace
S=load("X_pitch_1.mat");
X=deal(S.X);

% Paramètres 
length_min  = pyrunfile("pitch_mapping.py","length_min",parameters = X)
length_max  = pyrunfile("pitch_mapping.py","length_max",parameters = X)

% labels
S=load("labels_pitch_1.mat");
label=transpose(deal(S.labels_pitch_1));
svm_1=CODES.fit.svm(X,label);


for i=2:80
    %Calcul d'un nouveau sample
    x_mm=CODES.sampling.mm(svm_1,[0 length_min],[1 length_max]);
    %Calcul de son label
    X_label = [X(end,:);x_mm];
    labels  = transpose(double(pyrunfile("pitch_mapping.py","labels",parameters = X_label)))
    label = [label;labels(end)]
    X=[X; x_mm]
    %Calcul de la SVM
    svm_1=CODES.fit.svm(X,label);    
end


figure('Position',[200 200 500 500])
svm_0.isoplot
hold on 
svm_1.isoplot

%--------------------------------------------------------------------
% Mapping avec pitch 2

% Échantillons dans l'espace
S=load("X_pitch_2.mat");
X=deal(S.X);

% Paramètres 
length_min  = pyrunfile("pitch_mapping.py","length_min",parameters = X)
length_max  = pyrunfile("pitch_mapping.py","length_max",parameters = X)

% labels
S=load("labels_pitch_2.mat");
label=transpose(deal(S.labels_pitch_2));
svm_2=CODES.fit.svm(X,label);


for i=2:80
    %Calcul d'un nouveau sample
    x_mm=CODES.sampling.mm(svm_2,[0 length_min],[1 length_max]);
    %Calcul de son label
    X_label = [X(end,:);x_mm];
    labels  = transpose(double(pyrunfile("pitch_mapping.py","labels",parameters = X_label)))
    label = [label;labels(end)]
    X=[X; x_mm]
    %Calcul de la SVM
    svm_2=CODES.fit.svm(X,label);    
end

figure('Position',[200 200 500 500])
svm_0.isoplot
hold on 
svm_1.isoplot
hold on 
svm_2.isoplot


%--------------------------------------------------------------------
% Mapping avec pitch 3

% Échantillons dans l'espace
S=load("X_pitch_3.mat");
X=deal(S.X);

% Paramètres 
length_min  = pyrunfile("pitch_mapping.py","length_min",parameters = X)
length_max  = pyrunfile("pitch_mapping.py","length_max",parameters = X)

% labels
S=load("labels_pitch_3.mat");
label=transpose(deal(S.labels_pitch_2));
svm_2=CODES.fit.svm(X,label);


for i=2:80
    %Calcul d'un nouveau sample
    x_mm=CODES.sampling.mm(svm_2,[0 length_min],[1 length_max]);
    %Calcul de son label
    X_label = [X(end,:);x_mm];
    labels  = transpose(double(pyrunfile("pitch_mapping.py","labels",parameters = X_label)))
    label = [label;labels(end)]
    X=[X; x_mm]
    %Calcul de la SVM
    svm_2=CODES.fit.svm(X,label);    
end

%--------------------------------------------------------------------
% Mapping avec pitch 4

%--------------------------------------------------------------------
% Mapping avec pitch 5

%--------------------------------------------------------------------
% Mapping avec pitch 6

%--------------------------------------------------------------------
% Mapping avec pitch 7

%--------------------------------------------------------------------
% Mapping avec pitch 8

%--------------------------------------------------------------------
% Mapping avec pitch 9

%--------------------------------------------------------------------
% Mapping avec pitch 10
