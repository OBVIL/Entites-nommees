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
À lancer: <code> python brat-to-csv-interAnnotateurs.py <dossier_corpus> <fichier_output></code>

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
À lancer: <code>python calcul-score.py <input_file></code>

#### comparer-gold-et-predictions.pl
Regroupez les annotations de l'étalon-or avec les prévisions. Générer des fichiers TSV.
il faut que les fichiers sont rangés dans les dossiers intitulés Gold\_X et Predictions\_X.
Par example:
```
input_dossier
├── Predictions_LVP
|   └── Predictions_chapitre1.bios.tsv
└── Gold_LVP
    └── Gold_chapitre1.bios.tsv
 ```
 Usage: <code>perl stitch.pl <input_dossier> </code>
 Les fichiers de sortie sont déposés dans le même dossier où se trouvent les dossiers d'entrée.

#### evaluer_predictions.py
Ce script utilise nervaluate pour calculer la précision et le rappel
du marquage automatique des entités nommées par rapport à un étalon-or. 
Il faut fournir les fichiers à évaluer sous la forme suivante:
```
TOKEN   NE-COARSE-LIT   GOLD
Deux    O   O
mois    O   O
```
Les fichiers sous cette forme peuvent être creer par comparer-gold-et-predictions.pl.
Usage: <code>python evaluer-predictions.py <dossier_input> <fichier_output></code>

#### metrics.py
Calcul des métriques précision / rappel / fmesure sur deux textes donnés.
Usage : <code> python metrics.py <gold_file> <pred_file> --precision --rappel --fmesure</code>
Pour installer 'scikit-learn' (penser à vérifier sa version de python!)
<code>python -m pip install --user scikit-learn</code>
Affiche les résultats sur la sortie standard.
Le format d'entrée, est le conll définit par Inception:
```    Format WebAnoo TSV 3.x
    Exemple
    #Text=— Comme vous êtes changé ! Vous avez gagné de l’air. Paris vous fait du bien. Allons, racontez-moi les nouvelles.
    17-1	3680-3681	—	_	_	_	_	_	_	_
    17-2	3682-3687	Comme	_	_	_	_	_	_	_
    17-3	3688-3692	vous	_	_	_	_	_	_	_
    17-4	3693-3697	êtes	_	_	_	_	_	_	_
    17-5	3698-3704	changé	_	_	_	_	_	_	_
    17-6	3705-3706	!	_	_	_	_	_	_	_
    17-7	3707-3711	Vous	_	_	_	_	_	_	_
    17-8	3712-3716	avez	_	_	_	_	_	_	_
    17-9	3717-3722	gagné	_	_	_	_	_	_	_
    17-10	3723-3725	de	_	_	_	_	_	_	_
    17-11	3726-3727	l	_	_	_	_	_	_	_
    17-12	3727-3728	’	_	_	_	_	_	_	_
    17-13	3728-3731	air	_	_	_	_	_	_	_
    17-14	3731-3732	.	_	_	_	_	_	_	_
    17-15	3733-3738	Paris	LOC	false	true	false	false	false	false
    17-16	3739-3743	vous	_	_	_	_	_	_	_
    17-17	3744-3748	fait	_	_	_	_	_	_	_
    17-18	3749-3751	du	_	_	_	_	_	_	_
    17-19	3752-3756	bien	_	_	_	_	_	_	_
    17-20	3756-3757	.	_	_	_	_	_	_	_
    17-21	3758-3764	Allons	_	_	_	_	_	_	_
    17-22	3764-3765	,	_	_	_	_	_	_	_
    17-23	3766-3778	racontez-moi	_	_	_	_	_	_	_
    17-24	3779-3782	les	_	_	_	_	_	_	_
    17-25	3783-3792	nouvelles	_	_	_	_	_	_	_
    17-26	3792-3793	.	_	_	_	_	_	_	_
```
Vérifier la variable TAGSET en bas du fichier, pour faire correspondre les tags avec le bon chiffre. C'est à dire, qu'il faut modifier le nom des tags en accord avec son jeu de données.
Le chiffre est juste une équivalence pour scikit-learn.
Si par exemple, le jeu de données contient les tags "Personnage" et "Lieu" alors:
```    TAGSET = {
        '_': 0,
        'Personnage': 1,
        'Lieu': 2
     }
```


