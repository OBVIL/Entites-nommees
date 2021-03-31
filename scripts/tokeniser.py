# -*- coding: UTF-8 -*-

import os, stanza

nlp = stanza.Pipeline(lang='fr', processors='tokenize')
location = 'texts/'
for r, d, f in os.walk(location):
	for item in f:
		if item.endswith('.txt'):
			with open(os.path.join(r, item)) as fn:
				fop = open(str(os.path.join(r, item))+".tok", "w")
				print(item)
				lines = fn.readlines()
				for texte in lines:
					doc = nlp(texte.strip())
					for sent in doc.sentences:
						for token in sent.tokens:
							fop.write(token.text+"\n")
				fop.close()
   