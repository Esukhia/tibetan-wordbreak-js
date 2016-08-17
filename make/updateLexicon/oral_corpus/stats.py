from PyTib.common import non_tib_chars, open_file, write_file, tib_sort
import os
import re
from collections import defaultdict
import xlsxwriter
import time

corpus_path = '/home/drupchen/PycharmProjects/tibetan-wordbreak-js/make/updateLexicon/oral_corpus/files/'
list_of_words = []
for folder in os.listdir(corpus_path):
    for f in os.listdir(corpus_path+folder):
        content = open_file(corpus_path+folder+'/'+f).split('\n')
        content = [a.strip() for a in content if a != '']
        # find all non-tibetan characters
        to_delete = []
        for c in content:
            for char in c:
                if char not in to_delete and non_tib_chars(char):
                    to_delete.append(char)
        # add punctuation to be deleted
        to_delete.extend(['།', '༎', '༄', '༅'])

        # replace them with spaces
        text = []
        for r in range(len(content)-1):
            line = content[r]
            for t in to_delete:
                line = line.replace(t, ' ')
            text.append(re.sub(r'\s+', r' ', line))

        words = []
        for t in text:
            words.extend([u.rstrip('་')+'་' for u in t.split(' ') if u.rstrip('་') != ''])
        list_of_words.extend(words)

corpus_frequency = defaultdict(int)
for word in list_of_words:
    corpus_frequency[word] += 1

workbook = xlsxwriter.Workbook('stats/oral_corpus_stats_{}.xlsx'.format(time.strftime("%Y-%m-%d_%H:%M")))
format = workbook.add_format()
format.set_font_size(18)
format.set_font_name('Monlam Uni OuChan2')

frequency_sorted = [(corpus_frequency[a], a) for a in corpus_frequency]
frequency_sorted = sorted(frequency_sorted, key= lambda x: x[0], reverse=True)
worksheet1 = workbook.add_worksheet('ཚིག་རྒྱུག་ཆེ་ཆུང་།')

row = 0
col = 0
for frequency, word in (frequency_sorted):
    worksheet1.write(row, col, frequency)
    worksheet1.write(row, col + 1, word)
    row += 1

alpha_sorted = [(a, corpus_frequency[a]) for a in tib_sort(corpus_frequency)]
worksheet2 = workbook.add_worksheet('ཀ་ཁའི་གོ་རིམ།')

row = 0
col = 0
for word, frequency in (alpha_sorted):
    worksheet2.write(row, col,     frequency)
    worksheet2.write(row, col + 1, word)
    row += 1

workbook.close()
