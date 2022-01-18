### Projet Entités Nommées (OBVIL): 2019-2020
Ce dépôt contient toutes les données du projet des Entités nommées du labex OBVIL.
Ce travail, effectué entre 2019 et 2020 est amorcé par Motasem Alrahabi (OBVIL), en collaboration avec Carmen Brando (EHESS), Francesca Frontini (ILC, Italie) et des membres de l'équipe OBVIL: Romain Jalabert, Arthur Provenier, Marguerite Bordry, Camille Koskas et James Gawley. 

Le travail effectué consiste à: 
1. Définir un guide d'annotation manuelle des entités nommées pour les textes littéraire (romans...) --> [lien](https://hal.archives-ouvertes.fr/hal-03156278)
2. Créer un corpus de référence à partir, dans un premier temps, d'une annotation manuelle de trois romans: Le ventre de Paris de Zola, Nana de Zola et Bel ami de Maupassant,
3. Evaluer l'accord inter-annotateurs sur un sous-ensemble du corpus avec deux annotateurs experts du domaine littéraire en vue d'assurer une homogénéité au niveau des annotations,
4. Tester et évaluer trois modèles de REN: Spacy, Stanza et L3i NERC-EL.

### Arbre de fichiers
```
├── corpus-annotations-golds		<-les annotations finis (convertir avec script 0)
│   ├── belAmi
│   ├── LVP
│   └── Nana
├── corpus-plusieurs-annotateurs	<-les annotations des annotateurs (convertir avec script 0 et comparer avec 1 & 2)
│   ├── lvp
│   │   ├── lvp-zola-c
│   │   └── lvp-zola-m
│   └── nana
│       ├── nana-zola-c
│       └── nana-zola-m
├── documents				<-les instructions données aux annotateurs
├── evaluation				
│   ├── L3i_NERC-EL			<-les annotations L3i
│   │   ├── belAmi
│   │   ├── LVP
│   │   └── Nana
│   └── spacy				<-les annotations spacy (géneré par script 3)
│   │   ├── belAmi
│   │   ├── LVP
│   │   └── Nana
│   └── stanza				<-les annotations stanza (géneré par script 4)
│   │   ├── belAmi
│   │   ├── LVP
│   │   └── Nana
│   └── texts			<- text lis par spacy et stanza
├── publications
└── scripts				<-scripts qui génèrent des scores et predictions, et convertissent entre fomats
```

### Les Scripts

#### 0-transformer-brat-a-bios.pl
Transformer les fichiers dans /corpus-annotations-gold du format .ann en format .bios.tsv. 
Ceci n'est nécessaire que lorsque les annotations gold pour LVP et Nana ont été mises à jour. 
L'option --replace supprime automatiquement les anciens fichiers .bios.tsv 
situé sous évaluation/L3i-NERC-EL/comparateur-prédictions-et-or afin que 
ils puissent être utilisé par le script "comparer-gold-et-predictions.pl".

À lancer: <code> perl 0-transformer-brat-a-bios.pl <dossier_corpus> [OPTIONS]</code>
Par example:
<code> perl 0-transformer-brat-a-bios.pl corpus-annotations-golds/Gold_LVP/* --replace</code>

#### 1-convertir-conll2002-a-csv.py
Convertir la sortie de Brat en un csv utilisable par le script
de calcul du score inter-annotateurs.
Sous-entend que les fichiers sont dans un dossier avec pour nom le titre du corpus.
Et à l'intérieur, les dossiers extraits de Connll 2002 au format "nomCorpus-auteur-nomAnnotateur"
Convertir la sortie de Brat en un csv utilisable par le script
de calcul du score inter-annotateurs.
Sous-entend que les fichiers sont dans un dossier avec pour nom le titre du corpus.
À lancer: <code> python brat-to-csv-interAnnotateurs.py <dossier_corpus> <fichier_output></code>
Et à l'intérieur, les dossiers extraits de Brat au format "nomCorpus-auteur-nomAnnotateur"
À lancer:
D'abord, convertir les fichiers dans le dossier de chaque annotateur:
<code> perl 0-transformer-brat-a-bios.pl <dossier_corpus> </code>
Exécutez ensuite le script pour comparer les annotateurs :
<code> python 1-convertir-conll2002-a-csv.py <dossier_input> <dossier_output> </code>

```
lvp
├── lvp-zola-camille
│   ├── chapitre1.bios.tsv
│   ├── chapitre2.bios.tsv
└── lvp-zola-marguerite
    ├── chapitre1.bios.tsv
    ├── chapitre2.bios.tsv
```
Par example:
<code>
perl scripts/0-transformer-brat-a-bios.pl corpus-plusieurs-annotateurs/lvp/lvp-zola-c/* --skip-verification
perl scripts/0-transformer-brat-a-bios.pl corpus-plusieurs-annotateurs/lvp/lvp-zola-m/* --skip-verification
python scripts/1-convertir-conll2002-a-csv.py corpus-plusieurs-annotateurs/lvp corpus-plusieurs-annotateurs/output.csv</code>

#### 2-calcul-accord-interannotateur-de-csv.py
Calcul du score inter-annotateur. Prend en entrée les fichiers créés par 1-convertir-conll2002-a-csv.py.
À lancer: <code>python 1-convertir-conll2002-a-csv.py input_file </code>

#### 3-annotate-Spacy.py
Utilizer Spacy pour generer les annotations automatiques ([voir le Spacy documentation](https://spacy.io/usage/linguistic-features#own-annotations)).
Les texts sont rangés dans evaluations/Spacy-Stanza/texts/, est les resultats du scripts 
seront être laissés dans les dossiers nommés apres les corpus, sous evaluations/Spacy-Stanza/.
À lancer: <code>python 3-annotate-Spacy.py</code>

#### 4-annotate-Stanza.py
Exactment le même comme 3-annotate-Spacy.py, mais avec Stanza en place de Spacy.
À lancer: <code>python 4-annotate-Stanza.py</code>

#### 5-generer-tsv-avec-gold-et-predictions.pl
Regroupez les annotations de l'étalon-or avec les prévisions. Générer des fichiers TSV.
Il faut que les fichiers sont en format ".bios.tsv". Il est nécessaire de spécifier un 
dossier contenant des fichiers annotés automatiquement et un dossier contenant des 
annotations de référence.

Vous pouvez spécifier un dossier pour recevoir les résultats, ou vous pouvez autoriser 
qu'ils soient laissés dans le dossier "gold" par défaut.


Par example:
 Usage: <code>perl scripts/5-generer-tsv-avec-gold-et-predictions.pl --gold evaluation/L3i_NERC-EL/comparer-predictions-et-gold/Gold_LVP --predictions evaluation/L3i_NERC-EL/comparer-predictions-et-gold/Predictions_LVP </code>
 Les fichiers de sortie sont déposés dans le même dossier où se trouvent les dossiers d'entrée.
Par défaut, le contenu du fichier evaluation/L3i_NERC-EL/comparer-predictions-et-gold/ est converti.

#### 6-evaluer-predictions-de-tsv.py
Ce script utilise [nervaluate](https://pypi.org/project/nervaluate/) pour calculer la précision et le rappel
du marquage automatique des entités nommées par rapport à un étalon-or. 
Il faut fournir les fichiers à évaluer sous la forme suivante:
```
TOKEN   NE-COARSE-LIT   GOLD	VALIDITY
Deux    O   O	1
mois    O   O	1
```
Les fichiers sous cette forme peuvent être creer par comparer-gold-et-predictions.pl.
Usage: <code>python 6-evaluer-predictions-de-tsv.py <dossier_input> <fichier_output></code>
Par défaut, le contenu du fichier <code>/evaluation/L3i_NERC-EL/comparer-predictions-et-gold/Predictions_vs_Gold_belAmi/</code> sont évalués.
