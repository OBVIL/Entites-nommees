'''
Ce script utilise nervaluate pour calculer la précision et le rappel
du marquage automatique des entités nommées par rapport à un étalon-or. 
Il recherche un dossier appelé "Predictions", qui doit contenir tous les fichiers à évaluer sous la forme suivante:

TOKEN   NE-COARSE-LIT   GOLD
Deux    O   O
mois    O   O
...

Les scores sont générés pour chaque fichier et enregistrés dans un dossier appelé "Scores".

'''

import os
import glob
from nervaluate import Evaluator

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

for input_file in glob.iglob(f"Predictions/*"):
    '''Passez en boucle dans le dossier "Prédictions"'''
    st_annotation = []
    gold_annotation = []
    # load the predictions and gold standard tags
    with open(input_file, 'r', encoding='utf-8') as fin:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            try:
                token, stanza, gold = line.split('\t')
            except ValueError:
                print(line)
            stanza = stanza.upper()
            # begin formatting the tags in the 'conll' format
            st_annotation.append(f"{token}\t{stanza}")
            gold_annotation.append(f"{token}\t{gold}")
    #finish 'conll' format
    true = '\n'.join(gold_annotation)
    pred_st = '\n'.join(st_annotation)
    # generate precision and recall report
    evaluator = Evaluator(true, pred_st, tags=['LOC', 'PER', 'MISC'], loader="conll")
    results, results_by_tag = evaluator.evaluate()
    # print to file
    output_file = "Scores/" + input_file.replace("Predictions/", "")
    with open(output_file, 'w', encoding="utf-8") as fout:
        pretty_print(results, outfile=fout)