### Projet Entités Nommées (OBVIL): 2019-2020
Ce dépôt contient toutes les données du projet des Entités nommées du labex OBVIL.
Ce travail, effectué entre 2019 et 2020 est amorcé par Motasem Alrahabi (OBVIL), en collaboration avec Carmen Brando (EHESS), Francesca Frontini (ILC, Italie) et des membres de l'équipe OBVIL: Romain Jalabert, Arthur Provenier, Marguerite Bordry, Camille Koskas et James Gawley.

Le travail effectué consiste à 
1. mettre en place un guide d'annotation manuelle pour les entités nommées pour les textes littéraire (romans...)
2. créer un corpus de référence à partir, dans un premier temps, d'une annotation manuelle de trois romans: Le ventre de Paris de Zola, Nana de Zola et Bel ami de Maupassant.
3. tester et évaluer trois modèles de REN: Spacy, Stanza et L3i NERC-EL.

### Arbre de fichiers
```
├── Corpus de re201ference        <- contient les romans en format texte
│   ├── Maupassant-Bel-ami
│   ├── Zola-LVP
│   └── Zola-Nana
├── Evaluation                    <- les fichiers concernés avec comparison entre les predictions et realité. 
│   ├── L3i\ NERC-EL
│   │   ├── Gold
│   │   ├── Predictions
│   │   └── Predictions_vs_Gold   <- fichiers tsv énumérants les predictions et vrai balises pour chaque mot
│   └── Spacy-Stanza
│       ├── Bel-Ami-Maupassant
│       │   ├── LOC
│       │   ├── MISC
│       │   └── PER
│       ├── LVP-Zola
│       │   ├── LOC
│       │   ├── MISC
│       │   └── PER
│       └── Nana-Zola
│           ├── LOC
│           ├── MISC
│           └── PER
├── Guide\ d'annotation
│   └── Inter-Annotateurs
│       ├── annotateur-c
│       │   ├── lvp-zola-c
│       │   └── nana-zola-c
│       └── annotateur-m
│           ├── lvp-zola-m
│           └── nana-zola-m
├── Publication
└── Scripts
    ├── conversion                 <- touts les scripts sur conversion des formats
    └── evaluation                 <- touts les scripts pour mesurant le suces
```
### Les Scripts
#### brat-to-csv-interAnnotateurs.py
Convertir la sortie de Brat en un csv utilisable par le script
de calcul du score inter-annotateurs.
Sous-entend que les fichiers sont dans un dossier avec pour nom le titre du corpus.
À lancer: <code> python brat-to-csv-interAnnotateurs.py <corpus_dossier> <output_fichier></code>

Et à l'intérieur, les dossiers extraits de Brat au format "nomCorpus-auteur-nomAnnotateur"
Par example:
<code> python brat-to-csv-interAnnotateurs.py ../lvp ../lvp/output.csv</code>
```
lvp
├── lvp-zola-camille
│   ├── chapitre1.ann
│   ├── chapitre1.txt
   └── chapitre6.txt
└── lvp-zola-marguerite
    ├── chapitre1.ann
    ├── chapitre1.txt
```
#### calcul-score.py
Calcul du score inter-annotateur. Prend en entrée les fichiers créés par brat-to-csv-interAnnotateurs.py.
À lancer: <code>python calcul-score.py input_file</code>

#### 
