#!/usr/bin/env python

"""
    Calcul des métriques précision / rappel / fmesure sur deux textes donnés.
    Se base sur la bibliothèque 'scikit-learn' (https://scikit-learn.org/stable/modules/model_evaluation.html)

    Le format d'entrée, est le conll définit par Inception
    Format WebAnoo TSV 3.x
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

    Vérifier la variable TAGSET en bas du fichier, pour faire correspondre les tags avec le bon chiffre. C'est à dire, qu'il faut modifier le nom des tags en accord avec son jeu de données.
    Le chiffre est juste une équivalence pour scikit-learn.
    Si par exemple, le jeu de données contient les tags "Personnage" et "Lieu" alors:
    TAGSET = {
        '_': 0,
        'Personnage': 1,
        'Lieu': 2
     }

    Usage : python metrics.py gold_file pred_file --precision --rappel --fmesure

    Pour installer 'scikit-learn' (penser à vérifier sa version de python!)

        python -m pip install --user scikit-learn

    Affiche les résultats sur la sortie standard
"""

import sys
import argparse
import re

from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score

RE_CLEAN_TAG = re.compile(r"\[.+$")

def get_annotations_from_webanno(filename, tagset):
    """Renvoie une liste contenant les tags de chaque token
    par ordre d'apparition"""

    tags = []
    with open(filename, 'r', encoding="utf-8") as fin:
        for line in fin:

            line = line.strip()
            if not line or line.startswith('#'):
                continue

            try:
                tag_clean = RE_CLEAN_TAG.sub('', line.split('\t')[3])
                tags.append(tagset[tag_clean])
            except ValueError:
                continue

    return tags


def is_same_size(gold_set, pred_set):
    """Vérifie que les deux set sont de la même taille"""

    return len(gold_set) == len(pred_set)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Calcul des scores sur l'annotation des NER")
    parser.add_argument("gold_file",
                        help="Chemin vers le fichier goldstandard au format WebAnno")
    parser.add_argument("pred_file",
                        help="Chemin vers le fichier à prédire")
    parser.add_argument('--precision', action='store_true',
                        help="Calcul de la précision")
    parser.add_argument('--rappel', action='store_true',
                        help="Calcul du rappel")
    parser.add_argument('--fmesure', action='store_true',
                        help="Calcul de la fmesure")

    args = parser.parse_args()

    # Revoir ici
    TAGSET = {
            '_': 0,
            'LOC': 1,
            'PERS': 2,
            'MISC': 3
            }

    y_true = get_annotations_from_webanno(args.gold_file, TAGSET)
    y_pred = get_annotations_from_webanno(args.pred_file, TAGSET)

    if not is_same_size(y_true, y_pred):
        sys.exit(f"Les deux sets n'ont pas la même taille. Fin du programme")

    if args.precision:
        print(f"Précision: {precision_score(y_true, y_pred, average='macro')}")
    if args.rappel:
        print(f"Rappel: {recall_score(y_true, y_pred, average='macro')}")
    if args.fmesure:
        print(f"F-mesure: {f1_score(y_true, y_pred, average='macro')}")

