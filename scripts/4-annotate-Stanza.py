# -*- coding: UTF-8 -*-

import stanza, os
location = 'evaluations/Spacy-Stanza/texts/'
nlp = stanza.Pipeline(lang='fr', processors='tokenize,ner', tokenize_pretokenized=True)
for r, d, f in os.walk(location):
	for item in f:
		if item.endswith('.tok'):
			with open(os.path.join(r, item)) as fn:
				fop = open(str(os.path.join(r, item))+".stanza.bios.tsv", "w")
				print(item)
				words = [[line.strip() for line in fn]]
				#print(words)
				doc = nlp(words)
				for sent in doc.sentences:
					for token in sent.tokens:
						fop.write(token.text+"\t"+token.ner+"\n")
				fop.close()