# Entraîner un modèle Spacy

## Générer une configuration Spacy

Se référer à la documentation Spacy : https://spacy.io/usage/training/ ici, on
propose un exemple de réentraînement.

La commande pour générer le fichier de configuration qui sera utilisé pour
l'entraînement :

```
python -m spacy init fill-config base_config.cfg config.cfg
```

La commande _générique_ pour entraîner un nouveau modèle spacy. À noter que les
options peuvent être renseignées dans le fichier `config.cfg`. Le terminal
permet de surcharger les valeurs renseignées dans le fichier de configuration :

```
spacy train config.cfg -o new_pipeline --paths.train train.spacy --paths.dev dev.spacy
```

Afin de créer les fichiers binaires utilisés par Spacy, il faut d'abord lancer
un script de conversion des fichiers BRAT vers le format binaire de spacy
`docBin`. Le script `brat2spacy` utilise pour le moment
[SEM](github.com/YoannDupont/SEM) pour effectuer les conversions. Cela changera
avec les futures versions :

```
python ./brat2spacy.py ../corpus-annotations-golds/Gold_LVP/*.ann ../corpus-annotations-golds/Gold_Nana/*.ann ./lvp+nana-no_evoq.spacy --no-evoq
```

Il est alors possible de lancer la commande pour générer un nouveau modèle :

```
spacy train config.cfg -o v3.2/spacy_LVP+Nana-no_evoq --paths.train ./lvp+nana-no_evoq.spacy --paths.dev ./lvp+nana-no_evoq.spacy
```
