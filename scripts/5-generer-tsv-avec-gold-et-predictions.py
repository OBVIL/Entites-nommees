"""description:
  Regroupe les annotations de l'étalon-or avec les prédictions. Les fichiers
  TSV générés peuvent servir à calculer précision, rappel et F-mesure.

  Les fichiers étalon et prévision sont des TSV avec au minimum deux colonnes.
  l'extension attendue de ces fichiers est '.bios.tsv'. Les fichiers ayant une
  autre extension seront ignorés. Seules les deux premières colonnes seront
  considérées par le script. Les fichiers étalon et prévision doivent être en
  nombre égal et avoir les mêmes suffixes. On attend que les fichiers étalon
  aient un préfixe 'Gold_' et les fichiers prévision 'Predictions_'.

  Un example de hiérarchie de fichier pour le script:
  ├── Predictions_LVP
  │   ├── Predictions_chapitre1.bios.tsv
  │   └── Predictions_chapitre2.bios.tsv
  └── Gold_LVP
      ├── Gold_chapitre1.bios.tsv
      └── Gold_chapitre2.bios.tsv

  Où chaque fichier aura au moins deux colonnes, une contenant les tokens et
  l'autre les annotations au format BIOES:
      token1	O
      token2	S-Label1
      token3	O

      token4	B-Label2
      token5	E-Label2
      [...]

  Les fichiers de sortie auront alors la forme suivante:
      TOKEN	PREDICTION	GOLD	VALIDITY
      token1	O	O	1
      token2	S-LABEL1	S-LABEL1	1
      token3	O	O	1
      token4	B-LABEL2	S-LABEL2	0
      token5	E-LABEL2	O	0
      [...]

  Considérons que vous avez donné 'eval_LVP' comme répertoire de sortie. La
  hiérarchie de fichier finale aura alors la forme:
  ├── Predictions_LVP
  │   ├── Predictions_chapitre1.bios.tsv
  │   └── Predictions_chapitre2.bios.tsv
  └── Gold_LVP
  │   ├── Gold_chapitre1.bios.tsv
  │   └── Gold_chapitre2.bios.tsv
  └── eval_LVP
      ├── Predictions_chapitre1.predictions_vs_gold.tsv
      └── Predictions_chapitre2.predictions_vs_gold.tsv

exemples d'utilisation:
  python 5-generer-tsv-avec-gold-et-predictions.py -h
  python 5-generer-tsv-avec-gold-et-predictions.py corpus-annotations-golds/Gold_LVP evaluation/L3i_NERC-EL/LVP
  python 5-generer-tsv-avec-gold-et-predictions.py corpus-annotations-golds/Gold_LVP evaluation/L3i_NERC-EL/LVP -o sortie
"""

import pathlib
import re
import os


def readconll(filepath, encoding="utf-8"):
    # tokens has 3 values: line numbers, tokens, labels
    # lines numbers are useful when there is a misalignment
    data = [[], [], []]
    with open(filepath, encoding=encoding) as input_stream:
        for lineno, line in enumerate(input_stream, 1):
            if not line.strip():
                continue
            if line.startswith('TOKEN	'):
                continue
            parts = line.strip().split()
            data[0].append(lineno)
            data[1].append(parts[0])
            data[2].append(parts[1])
    return data


def normalize_tag(tag):
    tag = tag.upper()

    if tag == "O":
        return tag

    flag = tag[0]
    label = tag[2:]
    prefixes = ["PER", "LOC", "ORG", "PROD", "MISC"]
    for prefix in prefixes:
        if label.startswith(prefix):
            return f"{flag}-{prefix}"

    return tag


def main(gold, predictions, output_directory=None):
    goldpath = pathlib.Path(gold)
    hyppath = pathlib.Path(predictions)
    output_directory = pathlib.Path(output_directory or predictions)

    try:
        os.makedirs(output_directory)
    except FileExistsError:
        pass

    goldfiles = sorted(goldpath.glob("Gold_*.bios.tsv"))
    hypfiles = sorted(hyppath.glob("Predictions_*.bios.tsv"))

    if len(goldfiles) != len(hypfiles):
        raise RuntimeError(
            f"Different number of gold and hypothesis files: {len(goldfiles)} vs {len(hypfiles)}"
        )

    for goldfile, hypfile in zip(goldfiles, hypfiles):
        print(f"hyp:  {hypfile}")
        print(f"gold: {goldfile}")
        lineno_g, tokens_g, labels_g = readconll(goldfile)
        lineno_h, tokens_h, labels_h = readconll(hypfile)
        labels_g = [normalize_tag(l) for l in labels_g]
        labels_h = [normalize_tag(l) for l in labels_h]
        len_g = len(lineno_g)
        len_h = len(lineno_h)
        diffcontents = False

        for i in range(max(len_g, len_h)):
            tok_g = tokens_g[i]
            tok_h = tokens_h[i]
            diffcontents = tok_g.lower() != tok_h.lower()
            if diffcontents:
                print(
                    f"Different tokens at lines gold@{lineno_g[i]} <> hyp@{lineno_h[i]}:"
                    f" expected '{tok_g}', got '{tok_h}'"
                )

        if len_g != len_h:
            print(f"Different number of lines: {len(lineno_g)} vs {len(lineno_h)}", file=sys.stderr)
            print("skipping...\n")
            continue

        name = re.sub(".bios.tsv$", ".predictions_vs_gold.tsv", hypfile.name, flags=re.M)
        outpath = output_directory / name
        print(f"out:  {output_directory / name}")
        print(f"len:  {len_g}")
        with open(outpath, "w", encoding="utf-8") as output_stream:
            output_stream.write("TOKEN	PREDICTION	GOLD	VALIDITY\n")
            for token, prediction_label, gold_label in zip(tokens_g, labels_h, labels_g):
                validity = int(prediction_label == gold_label)
                output_stream.write(f"{token}	{prediction_label}	{gold_label}	{validity}\n")
        print()


if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("gold", help="The input directory for gold data")
    parser.add_argument("predictions", help="The input directory for system data")
    parser.add_argument("-o", "--output-directory", help="The output directory")
    args = parser.parse_args()

    main(**vars(args))
    sys.exit(0)
