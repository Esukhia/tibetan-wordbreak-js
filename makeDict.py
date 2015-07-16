#!/usr/bin/env python3

import json
particles = {}
verbs = {}
words_remove = {}
error_words = {}
custom_words = {}
custom_rules = []
words = [{},{},{},{},{}]
verbs_ashung = {}
words_ashung = {}

with open("src/TDC_remove.txt", "r") as headWords:
    for line in headWords:
        word = line.rstrip('་\n').rstrip('་')
        words_remove[word] = True

with open("src/new_words.txt", "r") as headWords:
    for line in headWords:
        word = line.rstrip('་\n').rstrip('་')
        custom_words[word] = True

with open("src/custom_errors.txt", "r") as headWords:
    for line in headWords:
        word = line.rstrip('\n').rstrip('་')
        error_words[word] = True

with open("src/custom_rules.txt", "r") as headWords:
    for line in headWords:
        rule = line.rstrip('\n').split()
        custom_rules.append(rule)

with open("src/TDC.txt", "r") as headWords:
    for line in headWords:
        word = line.rstrip('\n').rstrip('་')
        nbTshegs = word.count('་')
        if nbTshegs < 4:
            if word in words_remove:
                continue
            words[nbTshegs+1][word] = True
            if word.endswith('འ') and word != 'འ' and len(word) > 1:
                words_ashung[word[:-1]] = True

with open("src/verbs.txt", "r") as headWords:
    for line in headWords:
        word = line.rstrip('\n')
        verbs[word] = True
        words[1].pop(word, None)
        words[1].pop(word+'་བ', None)
        words[1].pop(word+'་པ', None)
        if word.endswith('འ') and word != 'འ' and len(word) > 1:
            verbs_ashung[word[:-1]] = True
            words_ashung.pop(word[:-1], None)

with open("src/particles.txt", "r") as headWords:
    for line in headWords:
        nbTshegs = line.count('་')
        particles[line.rstrip('\n')] = True
        words[nbTshegs+1].pop(line.rstrip('\n'), None)

print('error_words = '+json.dumps(error_words, ensure_ascii=False)+';\n')
print('custom_rules = '+json.dumps(custom_rules, ensure_ascii=False)+';\n')
print('custom_words = '+json.dumps(custom_words, ensure_ascii=False)+';\n')
print('verbs_ashung = '+json.dumps(verbs_ashung, ensure_ascii=False)+';\n')
print('words_ashung = '+json.dumps(words_ashung, ensure_ascii=False)+';\n')
print('verbs = '+json.dumps(verbs, ensure_ascii=False)+';\n')
print('particles = '+json.dumps(particles, ensure_ascii=False)+';\n')
print('words[1] = '+json.dumps(words[1], ensure_ascii=False)+';\n')
print('words[2] = '+json.dumps(words[2], ensure_ascii=False)+';\n')
print('words[3] = '+json.dumps(words[3], ensure_ascii=False)+';\n')
print('words[4] = '+json.dumps(words[4], ensure_ascii=False)+';\n')
print('main();\n')
