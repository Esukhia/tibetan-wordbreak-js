from PyTib.common import non_tib_chars, open_file, write_file, tib_sort
import os
import re
from collections import defaultdict
import xlsxwriter
import time

def chars_to_delete(text):
    chars = []
    for c in text:
        for char in c:
            if char not in chars and non_tib_chars(char):
                chars.append(char)
    # add punctuation to be deleted
    chars.extend(['།', '༎', '༄', '༅', '༔', '༑'])
    return chars

corpus_path = '/home/drupchen/PycharmProjects/tibetan-wordbreak-js/make/updateLexicon/oral_corpus/files/'
corpus_frequency = defaultdict(int)
newspapers = {}
word_origin = defaultdict(list)

for folder in os.listdir(corpus_path):
    print(folder)
    newspapers[folder] = defaultdict(int)
    for f in os.listdir(corpus_path+folder):
        print('\t', f)
        content = open_file(corpus_path+folder+'/'+f).replace('༌', '་').split('\n')
        content = [a.strip() for a in content if a != '']
        # find all non-tibetan characters
        to_delete = chars_to_delete(content)

        # replace them with spaces
        text = []
        for r in range(len(content)):
            line = content[r]
            for t in to_delete:
                line = line.replace(t, ' ')
            text.append(re.sub(r'\s+', r' ', line))

        # split the line in words and add it to the persons and to the newspaper dict
        for t in text:
            split_line = [u.rstrip('་')+'་' for u in t.split(' ') if u.rstrip('་') != '']
            for word in split_line:
                clean_word = word.lstrip('་')
                # add the word in the corresponding newspaper dict
                newspapers[folder][clean_word] += 1
                # add the word with its path to the persons’ dict
                word_path = '{}/{}'.format(folder, f)
                if word_path not in word_origin[clean_word]:
                    word_origin[clean_word].append(word_path)
                # add the word to the total corpus frequency
                corpus_frequency[clean_word] += 1


workbook = xlsxwriter.Workbook('stats/oral_corpus_stats_{}.xlsx'.format(time.strftime("%Y-%m-%d_%H:%M")))
format = workbook.add_format()
format.set_font_size(18)
format.set_font_name('Monlam Uni OuChan2')


def add_sorted_data(dict_of_frequencies, data_name):
    def write_data(data, sheet_name):
        worksheet = workbook.add_worksheet(sheet_name)
        row = 0
        col = 0
        for frequency, word in data:
            worksheet.write(row, col, frequency)
            worksheet.write(row, col + 1, word)
            row += 1

    # a. frequency-sorted
    frequency_sorted = [(dict_of_frequencies[a], a) for a in dict_of_frequencies]
    frequency_sorted = sorted(frequency_sorted, key= lambda x: x[0], reverse=True)
    write_data(frequency_sorted, data_name + 'ཚིག་རྒྱུག་ཆེ་ཆུང་།')

    # b. alpha-sorted
    alpha_sorted = [(a, dict_of_frequencies[a]) for a in tib_sort(dict_of_frequencies)]
    write_data(alpha_sorted, data_name+'ཀ་ཁའི་གོ་རིམ།')


def words_location(dict_of_frequencies):
    def write_words(sorted_list, sheet_name):
        worksheet = workbook.add_worksheet(sheet_name)
        row = 0
        col = 0
        for word, origin in sorted_list:
            worksheet.write(row, col, word)
            for i in range(len(origin)):
                worksheet.write(row, col + i + 1, origin[i])
            row += 1

    # b. alpha-sorted
    alpha_sorted = [(a, dict_of_frequencies[a]) for a in tib_sort(dict_of_frequencies)]
    write_words(alpha_sorted, 'ཚིག་གི་བྱུང་ཁུངས།')
    # b.
    size_sorted = [(a, dict_of_frequencies[a]) for a in dict_of_frequencies]
    size_sorted = sorted(size_sorted, key=lambda x: len(x[0].split('་')), reverse=True)
    write_words(size_sorted, 'ཚིག་གི་རིང་ཐུང་།')

# 1. Words and their file of origin
print('writing words’ origin')
words_location(word_origin)
# 2. Total frequency
print('writing total frequency')
add_sorted_data(corpus_frequency, 'ཆ་ཚང་བའི་')
# 3. Website frequency
print('writing newspaper frequencies')
for news in newspapers.keys():
    add_sorted_data(newspapers[news], news)

print('closing the file')
workbook.close()
