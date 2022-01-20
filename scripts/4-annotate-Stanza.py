# -*- coding: UTF-8 -*-
"""description:
  Annote avec Stanza un ensemble de documents déjà tokenisés au format un mot par ligne.
"""

import re
import os
import pathlib

import stanza


def main(location='evaluation/texts/'):
    nlp = stanza.Pipeline(lang='fr', processors='tokenize,mwt,ner', tokenize_pretokenized=True)

    path = pathlib.Path(location)
    for filepath in sorted(path.glob("**/*.txt.tok")):
        with open(filepath, encoding="utf-8") as fn:
            words = [[line.strip() for line in fn]]

        doc = nlp(words)
        item2 = "Predictions_" + filepath.name[:-8] + ".bios.tsv"
        pathtouse = path.parent / "stanza" / filepath.parent.name / item2
        print(pathtouse)

        with open(pathtouse, "w", encoding="utf-8") as fop:
            for sent in doc.sentences:
                words, tags = zip(*[(t.text, t.ner) for t in sent.tokens])
                words = list(words)
                tags = list(tags)
                for text, ner in zip(words, tags):
                    fop.write(f"{text}\t{ner}\n")


if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "--location",
        default="evaluation/texts/",
        help="The input directory (default: %(default)s)"
    )
    args = parser.parse_args()

    main(**vars(args))
    sys.exit(0)
