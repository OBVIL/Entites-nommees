# -*- coding: UTF-8 -*-
# Documentation : https://spacy.io/usage/linguistic-features#own-annotations

import spacy
from spacy.gold import biluo_tags_from_offsets
from spacy.lang.fr import French
import glob, os
from spacy.tokens import Doc

location = 'texts/'

try:
	nlp = spacy.load('fr_core_news_sm')
except OSError:
	print("Do you have the spacy module fr_core_news_sm installed? If not run 'python -m spacy download fr_core_news_sm'")

def custom_tokenize(text):
	words = text.split('|')
	return Doc(nlp.vocab, words=words)
nlp.tokenizer = custom_tokenize

for r, d, f in os.walk(location):
	for item in f:
		if item.endswith('.tok'):
			with open(os.path.join(r, item)) as fn:
				fop = open(str(os.path.join(r, item))+".spacy.ner", "w")
				print(item)
				words = fn.read().replace('\n', '|')
				words = words[:-1] #remove last pipe
				#print(words)
				doc = nlp(words)
				#for ent in doc.ents:
				#	print((ent.text, ent.label_))
				
				entities = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
				tags = biluo_tags_from_offsets(doc, entities)
				#print(tags)
				
				count = 0
				for tok in words.split("|"):
					tag = str(tags[count])
					fop.write(str(tok)+"\t"+tag+"\n")
					count = count + 1
				fop.close()
				


