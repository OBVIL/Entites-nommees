"""description:
  Convertir la sortie de 0-transformer-brat-a-bios.pl en un csv utilisable par le script
  de calcul du score inter-annotateurs '2-calcul-accord-interannotateur-de-csv.py'.
  Sous-entend que les fichiers sont dans un dossier avec pour nom le titre du corpus.
  Et à l'intérieur, les dossiers extraits de Connll 2002 au format "nomCorpus-auteur-nomAnnotateur"

  lvp
  ├── lvp-zola-camille
  │   ├── chapitre1.bios.tsv
  │   └── chapitre2.bios.tsv
  └── lvp-zola-marguerite
      ├── chapitre1.bios.tsv
      └── chapitre2.bios.tsv
"""

import sys
import pathlib
import re
import csv


def main(corpus, outfile, scheme='bios', delimiter=';'):
    map_tag = {"PER": 0, "Personnage": 0, "LOC": 1, "Lieu": 1, "MISC": 2, "Misc": 2, "O": 4}
    annotations = []
    csv_header = ["token"]
    for path_corpus in [p for p in pathlib.Path(corpus).glob("*") if p.is_dir()]:
        annotateur = path_corpus.stem.split("-")[-1]
        csv_header.append(annotateur)
        annotation = []
        for conllfile in path_corpus.glob(f"*.{scheme}.tsv"):
            with open(conllfile, "r", encoding="utf-8") as fin:
                for line in fin:
                    line = line.strip()
                    if not line:
                        continue
                    annotation.append(line.split("\t"))
        annotations.append(annotation)

    # On itère sur la première sous-liste pour récupérer l'index d'un token
    # ensuite pour chaque annotation (=chaque sous-liste)
    # on extrait le token correspondant
    output = []
    for i in range(0, len(annotations[1])):
        # on ajoute le token une seule fois
        line = [annotations[0][i][0]]
        for y in range(len(annotations)):
            # ajout du tag
            tag = re.sub("[BILUES]-", "", annotations[y][i][1])
            line.append(map_tag[tag])
        output.append(line)

    with open(outfile, "w", encoding="utf-8") as fout:
        csv_writer = csv.writer(fout, delimiter=delimiter)
        csv_writer.writerow(csv_header)
        csv_writer.writerows(output)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("corpus", help="The input folder")
    parser.add_argument("outfile", help="The output file")
    parser.add_argument(
        "--scheme", default="bios", help="The chunking flag scheme file (default: %(default)s)"
    )
    parser.add_argument(
        "--delimiter", default=";", help="The delimiter for output CSV file (default: %(default)s)"
    )
    args = parser.parse_args()

    main(**vars(args))
    sys.exit(0)
