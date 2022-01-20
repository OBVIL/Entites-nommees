# -*- coding: UTF-8 -*-
"""description:
  Annote avec Spacy un ensemble de documents déjà tokenisés au format un mot par ligne.
"""

import pathlib
import re

# Documentation : https://spacy.io/usage/linguistic-features#own-annotations
import spacy
from spacy.training.iob_utils import biluo_tags_from_offsets
from spacy.tokens import Doc


def custom_tokenize(nlp):
    def tokenize(text):
        words = text.split('|')
        return Doc(nlp.vocab, words=words)
    return tokenize


def bioes(tags):
    for i in range(len(tags)):
        if tags[i][0] == "U":
            tags[i] = "S" + tags[i][1:]
        elif tags[i][0] == "L":
            tags[i] = "E" + tags[i][1:]
    return tags


def main(location="evaluation/texts/", spacy_model='fr_core_news_sm'):
    try:
        nlp = spacy.load(spacy_model)
    except OSError as err:
        raise OSError(
            f"Do you have the spacy module '{spacy_model}' installed?"
            f" If not run 'python -m spacy download {spacy_model}'"
        ) from err

    nlp.tokenizer = custom_tokenize(nlp)

    path = pathlib.Path(location)
    for filepath in sorted(path.glob("**/*.txt.tok")):
        with open(filepath, encoding="utf-8") as fn:
            words = fn.read().replace('\n', '|').rstrip('|')

        doc = nlp(words)
        entities = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
        tags = bioes(biluo_tags_from_offsets(doc, entities))
        item2 = "Predictions_" + filepath.name[:-8] + ".bios.tsv"
        pathtouse = path.parent / "spacy" / filepath.parent.name / item2
        print(pathtouse)

        with open(pathtouse, "w", encoding="utf-8") as fop:
            for tok, tag in zip(words.split("|"), tags):
                fop.write(f"{tok}\t{tag}\n")


if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "--location",
        default="evaluation/texts/",
        help="The input directory where every file will be tagged (default: %(default)s)"
    )
    parser.add_argument(
        "--spacy-model",
        default="fr_core_news_sm",
        help="The spacy model to use (default: %(default)s)"
    )
    args = parser.parse_args()

    main(**vars(args))
    sys.exit(0)
