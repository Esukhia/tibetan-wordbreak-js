import PyTib
from PyTib.common import non_tib_chars, open_file, write_file, tib_sort, bisect_left
import os
import re
in_path = 'input/'
out_path = 'output/'

new = []
for f in os.listdir(in_path):
    content = open_file(in_path+f).replace('༌', '་').split('\n')
    content = [a.strip() for a in content if a != '']
    # find all non-tibetan characters
    to_delete = []
    for c in content:
        for char in c:
            if char not in to_delete and non_tib_chars(char):
                to_delete.append(char)
    # add punctuation to be deleted
    to_delete.extend(['།', '༎', '༄', '༅', '༑'])

    # replace them with spaces
    text = []
    for r in range(len(content)-1):
        line = content[r]
        for t in to_delete:
            line = line.replace(t, ' ')
        text.append(re.sub(r'\s+', r' ', line))

    lexicon = []
    for t in text:
        lexicon.extend([u.strip('་')+'་' for u in t.split(' ') if u.strip('་') != ''])
    new.extend(lexicon)
new = list(set(new))

oral_corpus_num = 0
extant_lexicon = []
extant_lexicon.extend(open_file('../updateJs/src/TDC.txt').split('\n'))
extant_lexicon.extend(open_file('../updateJs/src/verbs.txt').split('\n'))
extant_lexicon.extend(open_file('../updateJs/src/particles.txt').split('\n'))
for f in os.listdir('../updateJs/src/new_entries/'):
    extant_lexicon.extend(open_file('../updateJs/src/new_entries/'+f).split('\n'))
    number = int(f.split('.')[0].split('_')[2])
    if number > oral_corpus_num:
        oral_corpus_num = number

new_entries = [n for n in new if n not in extant_lexicon]

write_file(out_path+'all_entries{}.txt'.format(oral_corpus_num+1), '\n'.join(tib_sort(new)))
if new_entries:
    write_file('../updateJs/src/new_entries/recordings_{}.txt'.format(oral_corpus_num+1), '\n'.join(tib_sort(new_entries)))