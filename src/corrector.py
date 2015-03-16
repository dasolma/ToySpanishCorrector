#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re, collections, csv

def words(text): return re.findall('[a-záéíóúñü]+'.decode('utf-8'), text.decode('utf-8').lower())

def train(features):
    model = collections.defaultdict(lambda: 1)
    for f in features:
        model[f] += 1
    return model

def read_dict(files):
    data = ''
    for file in files:
        with open(file, 'r') as f:
            data += ' ' + f.read()

    return data


def read_frecuencies(file='../data/10000_formas.TXT', lemario_file='../data/lemario.txt', min = 0):
    frecuencies = {}

    lemario = words(open(lemario_file, "r").read())
    with open(file, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t', quotechar='|')
        next(reader, None)
        for row in reader:
            row = [r for r in row if len(r.strip()) > 0]
            if len(row) > 2 and len(row[0])>0:

                key = row[1].strip().decode('latin-1')
                frec = int(row[3].replace(".", ""))

                if frec > min and key in lemario:
                    frecuencies[key] = frec


    return frecuencies

def mix(f1, f2):
    for f in f2.keys():
        if f in f1: f1[f] = (f1[f] + f2[f])/2
        else: f1[f] = f2[f]

    return f1

NWORDS = train( words( read_dict(['../data/news.txt', '../data/conjugations.txt']) ) )
NWORDS = mix(NWORDS, read_frecuencies(min=2))

alphabet = 'abcdefghijklmnopqrstuvwxyzáéíóúñü'.decode('utf-8')



def edits1(word):
   splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
   deletes    = [a + b[1:] for a, b in splits if b]
   transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
   replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
   inserts    = [a + c + b     for a, b in splits for c in alphabet]
   return set(deletes + transposes + replaces + inserts)

def known_edits2(word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in NWORDS)

def unknown_edits2(word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if not e2 in NWORDS)


def known_edits3(word):
    return set(e2 for e1 in known_edits2(word) for e2 in edits1(e1) if e2 in NWORDS)

def known_edits4(word):
    return set(e2 for e1 in known_edits3(word) for e2 in edits1(e1) if e2 in NWORDS)

def known(words): return set(w for w in words if w in NWORDS)

def unknown(words): return set(w for w in words if not w in NWORDS)

def candidates(word):
    word = word.decode('utf-8')
    kn = known([word])
    if len(kn) > 0: return kn
    return (known(edits1(word)).union(known_edits2(word)))

def correct(word):
    cand = candidates(word)
    if len(cand) == 0: return []

    #take candidates and their frecuencies
    cand = [{'sug':c, 'frec':NWORDS[c]} for c in cand]

    #calculate accumulated frequency
    cand = sorted(cand, reverse=True)
    acu = 0
    for c in cand:
        acu += c['frec']
        c['frec_acu'] = acu

    '''
    #return the 80%
    if( len(cand) > 10):
        max = acu * 0.5
        cand = [c for c in cand if c['frec_acu'] < max]

        cand = cand[:10]
    '''


    return cand


'''
Mejoras:

  - errores comunes de teclado
  - creian -> creían (no crean): los cambios de tilde deben ser mas probables que los de letra
  - conjugaciones de los verbos. ¿las frecuencias deben ser comunes en todas las conjugaciones de un verbo?

'''