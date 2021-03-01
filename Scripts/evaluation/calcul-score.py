import sys
from nltk import agreement
import argparse

"""
    Calcul du score inter-annotateur

    - utilisation de la mesure Cohen Kappa pour deux annotateurs
    - utilisation de la mesure Fleiss Kappa pour trois annotateurs et plus
    Le choix du score se fait sur le nombre de colonnes.

    Le format de données est un csv, "Token;Annot1;Annot2;Annot_n"
    Les valeurs pour les annotations sont numériques.

    TOKEN;"Annotateur 1";"Annotateur 2"
    "NE 1";4;4
    "NE 2";1;4
    "NE 3";4;2
    "NE 4";1;0
    "NE 5";3;4

    Voir l'exemple 'Kappa.csv'.

    https://learnaitech.com/how-to-compute-inter-rater-reliablity-metrics-cohens-kappa-fleisss-kappa-cronbach-alpha-kripndorff-alpha-scotts-pi-inter-class-correlation-in-python/

    Usage : python calcul-score.py
    pip install --user nltk
"""

def print_agreement(score):
    # Voir si même interprétation cohen et fleiss
    if score < 0:
        print("Poor agreement")
    elif score >= 0.00 and score <= 0.20:
        print("Slight agreement")
    elif score > 0.20 and score <= 0.40:
        print("Fair agreement")
    elif score > 0.40 and score <= 0.60:
        print("Moderate agreement")
    elif score > 0.60 and score <= 0.80:
        print("Substantial agreement")
    elif score > 0.80 and score <= 1.00:
        print("Almost perfect agreement")

"""
if len(sys.argv) > 2:
    print("Usage : python calcul-score.py nom-corpus.csv")
    sys.exit(1)
else:
    input_file = sys.argv[1]
"""
# Modifier le nom du fichier ici
#input_file = "Kappa.csv"
parser = argparse.ArgumentParser(
    description="Calcul du score inter-annotateur. "
)
parser.add_argument('input', help="The input file")
arguments = parser.parse_args()
input_file = arguments.input

# Le séparateur par défaut est le point-virgule
# changer pour ne pas hardcoder ensuite
sep = ';'

data = []
is_cohen = False
is_fleiss = False
with open(input_file, 'r', encoding="utf-8") as csvfile:
    next(csvfile) # Suppose qu'il y a tjs un header
    for token_idx, line in enumerate(csvfile):
        line = line.strip()
        if not line:
            continue

        annotations = line.split(sep)[1:]
        if not is_cohen and not is_fleiss:
            if len(annotations) == 2:
                print("Nombre d'annotateurs: 2")
                is_cohen = True
            elif len(annotations) >= 3:
                print(f"Nombre d'annotateurs: {len(annotations)}")
                is_fleiss = True

        n_annotators = len(annotations)
        for i in range(0, n_annotators):
            data.append([i, token_idx, annotations[i]])

if is_cohen and is_fleiss:
    sys.exit('Problème dans le nombre de colonnes du csv')

ratingtask = agreement.AnnotationTask(data=data)

if is_cohen:
    kappa_cohen = ratingtask.kappa()
    print(f"Score de Kappa Cohen: {kappa_cohen}")
    print_agreement(kappa_cohen)

elif is_fleiss:
    kappa_fleiss = ratingtask.multi_kappa()
    print(f"Score de Kappa Fleiss: {kappa_fleiss}")
    print_agreement(kappa_fleiss)
