'''description:
  Ce script utilise nervaluate pour calculer la précision et le rappel
  du marquage automatique des entités nommées par rapport à un étalon-or. 
  Il recherche un dossier appelé "Predictions", qui doit contenir tous les fichiers à évaluer sous la forme suivante:

  TOKEN   NE-COARSE-LIT   GOLD   VALIDITY
  Deux    O   O   1
  mois    O   O   1
  ...

  Les scores sont générés pour chaque fichier et enregistrés dans un dossier appelé "Scores".
'''

from nervaluate import Evaluator
import pathlib
import contextlib
import sys


def pretty_print(result, outfile=None):
    """Affichage plus beau que par défaut"""
    x_name = ['Measure'] + [k for k in result]
    y_name = []
    rows = []
    for evaluation in result:
        metrics = result[evaluation]
        row = []
        for metric, score in metrics.items():
            if metric not in y_name:
                y_name.append(metric)
            row.append(round(score, 3)) # Arrondir
        rows.append(row)
    grid = [score for score in [column for column in zip(*rows)]]
    print(*x_name, sep='\t', file=outfile)
    for i, row in enumerate(grid):
        print(y_name[i], *map(str, row), sep='\t', file=outfile)


def main(input_folder, output_file="precision-et-rappel.csv", tagset=('LOC', 'PER', 'MISC')):
    actual = []
    predicted = []
    for input_file in pathlib.Path(input_folder).glob("*"):
        '''Passez en boucle dans le dossier "Prédictions"'''
        guess_annotation = []
        gold_annotation = []
        # load the predictions and gold standard tags
        with open(input_file, 'r', encoding='utf-8') as fin:
            for line in fin:
                line = line.strip()
                if not line:
                    continue
                try:
                    token, guess, gold, validity = line.split('\t')
                except ValueError:
                    print(line)
                    raise
                guess = guess.upper()
                # begin formatting the tags in the 'conll' format
                guess_annotation.append(f"{token}\t{guess}")
                gold_annotation.append(f"{token}\t{gold}")
        # finish 'conll' format
        actual.extend(gold_annotation)
        predicted.extend(guess_annotation)
    # generate precision and recall report
    evaluator = Evaluator('\n'.join(actual), '\n'.join(predicted), tags=tagset, loader="conll")
    results, results_by_tag = evaluator.evaluate()

    # print to file
    with open(output_file, "w", encoding="utf-8") as fout:
        pretty_print(results, outfile=fout)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        'input_folder',
        help="The input folder"
    )
    parser.add_argument(
        '--output-file',
        default="precision-et-rappel.csv",
        help="The output file (default: %(default)s)",
    )
    parser.add_argument(
        '--tagset',
        help="The tagset to use (default: %(default)s)",
        nargs="+",
        default=('LOC', 'PER', 'MISC'),
    )
    arguments = parser.parse_args()

    main(**vars(arguments))
