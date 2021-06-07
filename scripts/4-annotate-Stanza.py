# -*- coding: UTF-8 -*-
import re
import stanza, os
location = 'evaluation/texts/'
nlp = stanza.Pipeline(lang='fr', processors='tokenize,ner', tokenize_pretokenized=True)
for r, d, f in os.walk(location):
    for item in f:
        if item.endswith('.tok'):
            with open(os.path.join(r, item)) as fn:
                item2 = re.sub(".txt.tok", "", item)
                item2 = "Predictions_" + item2
                r2 = re.sub(".+(/.+?)$", "evaluation/stanza\\1", r)
                pathtouse = str(os.path.join(r2, item2))+".bios.tsv"
                fop = open(pathtouse, "w")
                print(pathtouse)
                words = [[line.strip() for line in fn]]
                #print(words)
                doc = nlp(words)
                for sent in doc.sentences:
                    for token in sent.tokens:
                        fop.write(token.text+"\t"+token.ner+"\n")
                fop.close()