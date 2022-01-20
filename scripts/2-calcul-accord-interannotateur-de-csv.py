"""description:
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

import sys
from nltk import agreement
from nltk.metrics import interval_distance, binary_distance
import argparse
import csv


def qualify_agreement(score):
    """Interpreration of the kappa taken from Landis & Koch (1977)."""

    if score < 0.00:
        return "Poor agreement"
    elif score <= 0.20:
        return "Slight agreement"
    elif score <= 0.40:
        return "Fair agreement"
    elif score <= 0.60:
        return "Moderate agreement"
    elif score <= 0.80:
        return "Substantial agreement"
    elif score <= 1.00:
        return "Almost perfect agreement"
    else:
        return "Agreement > 1, maybe there is a problem?"


def main(input_file, delimiter=';'):
    data = []
    is_cohen = False
    is_fleiss = False
    with open(input_file, 'r', encoding='utf-8') as input_stream:
        reader = csv.DictReader(input_stream, delimiter=delimiter)
        n_annotators = len(reader.fieldnames[1:])

        if n_annotators == 1:
            raise ValueError('Only one annotator.')
        else:
            is_cohen = n_annotators == 2
            is_fleiss = not is_cohen

        for token_idx, line in enumerate(reader):
            annotations = [line[key] for key in reader.fieldnames[1:]]
            if len(annotations) != n_annotators:
                raise ValueError(f"Wrong number of annotators for token {token_idx}. Expected : {n_annotators}, got: {len(annotations)}")
            if token_idx == 0:
                print(f"Annotator number: {n_annotators}")

            for i, annotation in enumerate(annotations):
                data.append([i, str(token_idx), int(annotation)])

    ratingtask = agreement.AnnotationTask(data=data, distance=binary_distance)

    print()
    if is_cohen:
        kappa_cohen = ratingtask.kappa()
        print(f"Cohen's κ: {kappa_cohen}")
        print(qualify_agreement(kappa_cohen))

    elif is_fleiss:
        kappa_fleiss = ratingtask.multi_kappa()
        print(f"Fleiss' κ: {kappa_fleiss}")
        print(qualify_agreement(kappa_fleiss))

    # krippendorf = ratingtask.alpha()
    # print()
    # print(f"Krippendorf's α: {krippendorf}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('input_file', help="The input file", default="../ann-to-csv-output.csv", nargs='?', const="../ann-to-csv-output.csv")
    parser.add_argument('-d', '--delimiter', help="The delimiter to use (default: %(default)s)", default=";")

    arguments = parser.parse_args()
    main(**vars(arguments))
    sys.exit(0)
