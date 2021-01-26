# Calculer le score depuis un corpus annoté avec Brat.

Voir la documentation dans les scripts si besoin.

## Installation

```
pip install --user nltk
```

## Scripts

```
anntoconll.py
brat-to-csv-interAnnotateurs.py
calcul-score.py
```

## 1. Récupération du script pour mettre au format conll

On récupère depuis le fork de Brat disponible sur le github de l'obvil.

```
git clone https://github.com/OBVIL/brat.git
cd brat/tools
```

## 2. Lancer la transformation
Sous-entend que les textes sont un dossier "lvp" contenant
un sous-dossier "lvp-zola-camille" et "lvp-zola-marguerite"

```
lvp
├── lvp-zola-camille
│   ├── chapitre1.ann
│   ├── chapitre1.txt
└── lvp-zola-marguerite
    ├── chapitre1.ann
    ├── chapitre1.txt
```

```
python anntoconll.py ../../lvp/lvp-zola-*/*.txt
cd ../..
```

## 3. Générer le format csv pour le calcul du score depuis conll
Modifier les chemins dans le script.
Par défaut, le fichier est sauvegardé dans un dossier `output`.

```
mkdir -p output
python brat-to-csv-interAnnotateurs.py
```

## 4. Calculer le score depuis le csv
Modifier les chemins dans le script. Le score s'affiche sur la sortie standard.

`python calcul-score.py`
