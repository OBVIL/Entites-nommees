"""Train a Spacy model from brat files, using attributes to create subclasses."""

import pathlib

import spacy
from spacy.tokens import DocBin

import sem.storage
import sem.processors


mapping = {
    "lieu": "LOC",
    "location": "LOC",
    "locname": "LOC",
    "loc": "LOC",
    "personnage": "PER",
    "person": "PER",
    "persname": "PER",
    "per": "PER",
    "misc": "MISC",
    "organization": "ORG",
    "org": "ORG",
    "date": "DATE",
    "hour": "HOUR",
    "event": "EVENT",
}


def make_examples(content, anns, sents):
    contents = []
    sent_anns = []

    for sent in sents:
        contents.append(content[sent.start: sent.end])
        sent_anns.append([(ann.start - sent.start, ann.end - sent.start, ann.value) for ann in anns if ann.span in sent])

    return zip(contents, sent_anns)


def main(files, outputfile, ignore_attributes=False, no_evoque=False):
    print("loading things...")
    nlp = spacy.load("fr_core_news_sm")
    segmenter = sem.processors.SegmentationProcessor("fr")

    print("processing data...")
    # the DocBin will store the example documents
    db = DocBin()
    for bratfile in sorted(files, key=lambda x: str(x).lower()):
        print(bratfile)
        tees = []
        attribs = []
        with open(bratfile) as input_stream:
            for line in input_stream:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split("\t")
                if len(parts) == 3:  # annotation
                    ident, annot, text = parts
                    label, bounds = annot.split(" ", 1)
                    offsets = bounds.split()
                    start = int(offsets[0])
                    end = int(offsets[-1])
                    tees.append([int(ident[1:]), label, start, end])
                elif len(parts) == 2:  # attribute
                    attribs.append(parts)
        tees.sort(key=lambda x: x[0])
        tmp = [None for _ in range(tees[-1][0]+1)]
        for i, t in enumerate(tees):
            tmp[t[0]] = t
        annots = []
        for t in tmp:#[1:]:
            if t is None:
                annots.append(None)
            else:
                ident, label, start, end = t
                label = mapping[label.lower()]
                annots.append(sem.storage.Tag(label, start, end))

        if no_evoque:
            attribs = [attrib for attrib in attribs if "evoque" not in attrib[-1].lower()]
        if not ignore_attributes:
            for parts in attribs:
                ident, val = parts
                value, tag = val.split(" ", 1)
                idx = int(tag[1:])#-1
                try:
                    annots[idx].value = annots[idx].value + "." + value
                except IndexError:
                    print(f"{idx} out of bounds: {len(annots)}")
                    present = set([t[0] for t in tees])
                    total = set(range(tees[-1][0]))
                    missing = total - present
                    print(missing)
        annots = [ann for ann in annots if ann is not None]

        with open(str(bratfile)[:-3] + "txt", newline="") as input_stream:
            text = input_stream.read()

        document = sem.storage.Document(name="", content=text)
        document.add_annotationset(sem.storage.AnnotationSet("NER", annotations=annots))

        segmenter.process_document(document)

        anns = sem.storage.get_bottom_level(document.annotationset("NER").char_offsets())
        sents = document.segmentation("sentences").char_offsets()
        training_data = make_examples(document.content, anns, sents)

        for text, annotations in training_data:
            doc = nlp(text)
            ents = []
            for start, end, label in annotations:
                span = doc.char_span(start, end, label=label)
                if span is not None:
                    ents.append(span)
            doc.ents = ents
            db.add(doc)

    print("saving...")
    db.to_disk(outputfile)
    print("done!")


def parse_cl(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "files",
        nargs="+",
        help="The .ann files"
    )
    parser.add_argument(
        "outputfile",
        help="The output file"
    )
    parser.add_argument(
        "--ignore-attributes",
        action="store_true",
        help="Ignore attributes to create fine-grained annotations."
    )
    parser.add_argument(
        "--no-evoque",
        action="store_true",
        help="Ignore 'Evoque' attributes."
    )
    args = parser.parse_args(argv)

    main(**vars(args))


if __name__ == "__main__":
    import sys

    parse_cl()
    sys.exit(0)
