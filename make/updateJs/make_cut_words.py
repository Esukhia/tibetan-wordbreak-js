#!/usr/bin/env python3

import json
import os

particles = {}
verbs = {}
words_remove = {}
error_words = {}
custom_words = {}
custom_rules = []
words = [{},{},{},{},{}]
verbs_ashung = {}
words_ashung = {}

with open("make/updateJs/src/TDC_remove.txt", "r") as headWords:
    for line in headWords:
        word = line.rstrip('་\n').rstrip('་')
        words_remove[word] = True

with open("make/updateJs/src/custom_errors.txt", "r") as headWords:
    for line in headWords:
        word = line.rstrip('\n').rstrip('་')
        error_words[word] = True

with open("make/updateJs/src/custom_rules.txt", "r") as headWords:
    for line in headWords:
        rule = line.rstrip('\n').split()
        custom_rules.append(rule)

lexicon = [
    'make/updateJs/src/TDC.txt',
    'make/updateJs/src/particles.txt',
]
for f in os.listdir('make/updateJs/src/new_entries/'):
    lexicon.append('make/updateJs/src/new_entries/'+f)

for l in lexicon:
    with open(l, "r") as headWords:
        for line in headWords:
            word = line.rstrip('\n').rstrip('་')
            nbTshegs = word.count('་')
            if nbTshegs < 4:
                if word in words_remove:
                    continue
                words[nbTshegs+1][word] = True
                if word.endswith('འ') and word != 'འ' and len(word) > 1:
                    words_ashung[word[:-1]] = True

with open("make/updateJs/src/verbs.txt", "r") as headWords:
    for line in headWords:
        word = line.rstrip('\n')
        verbs[word] = True
        words[1].pop(word, None)
        words[1].pop(word+'་བ', None)
        words[1].pop(word+'་པ', None)
        if word.endswith('འ') and word != 'འ' and len(word) > 1:
            verbs_ashung[word[:-1]] = True
            words_ashung.pop(word[:-1], None)

with open("make/updateJs/src/non-separate_particles.txt", "r") as headWords:
    for line in headWords:
        nbTshegs = line.count('་')
        particles[line.rstrip('\n')] = True
        words[nbTshegs+1].pop(line.rstrip('\n'), None)

data = ''
data += 'error_words = '+json.dumps(error_words, ensure_ascii=False)+';\n\n'
data += 'custom_rules = '+json.dumps(custom_rules, ensure_ascii=False)+';\n\n'
data += 'custom_words = '+json.dumps(custom_words, ensure_ascii=False)+';\n\n'
data += 'verbs_ashung = '+json.dumps(verbs_ashung, ensure_ascii=False)+';\n\n'
data += 'words_ashung = '+json.dumps(words_ashung, ensure_ascii=False)+';\n\n'
data += 'verbs = '+json.dumps(verbs, ensure_ascii=False)+';\n\n'
data += 'particles = '+json.dumps(particles, ensure_ascii=False)+';\n\n'
data += 'words[1] = '+json.dumps(words[1], ensure_ascii=False)+';\n\n'
data += 'words[2] = '+json.dumps(words[2], ensure_ascii=False)+';\n\n'
data += 'words[3] = '+json.dumps(words[3], ensure_ascii=False)+';\n\n'
data += 'words[4] = '+json.dumps(words[4], ensure_ascii=False)+';\n\n'
data += 'main();\n'

with open('cutWords.html', 'w', -1, 'utf-8') as f:
    # write the header of the html
    f.write('''<!DOCTYPE html><html lang="en">
<head><meta http-equiv="content-type" content="text/html; charset=UTF-8"><meta charset="utf-8"><meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title></title><meta name="viewport" content="width=device-width, initial-scale=1.0, maximal-scale=1.0, user-scalable=no, minimal-scale=1.0">
    <script type="text/javascript">\n''')
    # write the js code
    with open('make/updateJs/src/cutWords_code.js', 'r', -1, 'utf-8') as g:
        f.write(g.read()+'\n')
    f.write(data)
    # write the footer of the html
    f.write(''' </script>
</head>
<body>
  <button id="button" onclick="cutWordsInText()" style="font-size:20pt;width:150pt;">ཚིག་ གཏུབ།</button><br>
  <textarea id="text" style="width:100%;height:600pt;font-size:18pt;"></textarea>
</body></html>''')

with open('make/cutWords.js', 'w', -1, 'utf-8') as f:
    with open('make/updateJs/src/cutWords_code.js', 'r', -1, 'utf-8') as g:
        f.write(g.read()+'\n')
    f.write(data)
