from PyTib.common import non_tib_chars, open_file, tib_sort
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


def add_sorted_data(workbook, dict_of_frequencies, data_name):
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


def words_location(workbook, dict_of_frequencies):
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
    write_words(alpha_sorted, 'བྱུང་ཁུངས་ལ་ཀ་ཁའི་གོ་རིམ།')
    # b.
    size_sorted = [(a, dict_of_frequencies[a]) for a in dict_of_frequencies]
    size_sorted = sorted(size_sorted, key=lambda x: len(x[0].split('་')), reverse=True)
    write_words(size_sorted, 'བྱུང་ཁུངས་ལ་རིང་ཐུང་གི་གོ་རིམ།')


def processing_corpus(corpus_path):
    print('processing corpus')
    # variables for the main xslx
    corpus_frequencies = {}
    corpus_total_frequency = defaultdict(int)
    corpus_origin = defaultdict(list)

    # variables for individual xslx files
    persons_frequencies = {}
    persons_total_frequency = {}
    persons_origin = {}

    for f in os.listdir(corpus_path):
        # A. finding the names for the current file
        file_name = f
        # finding the name of the section
        section = ''
        for c in corpus_sections:
            if c in f:
                section = c
                file_name = file_name.replace(c, '')
        if section == '':
            section = 'ཁུངས་མེད།'
        # finding the name of the person
        person = re.sub(r'[0-9]* *\([0-9]+\).txt', '', file_name).strip()

        # B. initiating the entries in dicts if missing for the current file
        # creating an entry in corpus_frequencies{} if it does not exist
        if section not in corpus_frequencies.keys():
            corpus_frequencies[section] = defaultdict(int)

        # creating an entry in persons_frequencies{} if it does not exist
        if person not in persons_frequencies.keys():
            persons_frequencies[person] = {}
        if section not in persons_frequencies[person].keys():
            persons_frequencies[person][section] = defaultdict(int)

        # creating an entry in persons_total_frequency if it does not exist
        if person not in persons_total_frequency.keys():
            persons_total_frequency[person] = defaultdict(int)

        # creating an entry in persons_origin{} if it does not exist
        if person not in persons_origin.keys():
            persons_origin[person] = defaultdict(list)

        # C. processing the current file
        content = open_file(corpus_path+'/'+f).replace('༌', '་').split('\n')
        content = [a.strip() for a in content if a != '']

        # find all non-tibetan characters
        to_delete = chars_to_delete(content)
        # replace them with spaces
        text = []
        for r in range(len(content)):
            line = content[r]
            for t in to_delete:
                line = line.replace(t, ' ')
            text.append(re.sub(r'\s+', r' ', line).strip())

        # D. filling in the corpus and personal variables
        # split the line in words and add it to the persons_frequencies and to the newspaper dict
        for t in text:
            split_line = [u.rstrip('་')+'་' for u in t.split(' ') if u.rstrip('་') != '']
            for word in split_line:
                clean_word = word.lstrip('་')
                # corpus stats
                corpus_frequencies[section][clean_word] += 1
                corpus_total_frequency[clean_word] += 1
                if f not in corpus_origin[clean_word]:
                    corpus_origin[clean_word].append(f)

                # persons’ stats
                persons_frequencies[person][section][clean_word] += 1
                persons_total_frequency[person][clean_word] += 1
                if f not in persons_origin[person][clean_word]:
                    persons_origin[person][clean_word].append(f)

    return corpus_frequencies, corpus_total_frequency, corpus_origin, persons_frequencies, persons_total_frequency, persons_origin


def write_to_xlsx(output_name, origin, total_frequency, frequencies):
    print(output_name)
    workbook = xlsxwriter.Workbook('stats/{}_oral_corpus_stats_{}.xlsx'.format(output_name, time.strftime("%Y-%m-%d_%H:%M")))
    format = workbook.add_format()
    format.set_font_size(18)
    format.set_font_name('Monlam Uni OuChan2')

    # 1. Words and their file of origin
    print('\twriting words’ origin')
    words_location(workbook, origin)
    # 2. Total frequency
    print('\twriting total frequency')
    add_sorted_data(workbook, total_frequency, 'ཆ་ཚང་བའི་')
    # 3. Website frequency
    print('\twriting section frequencies')
    for section in frequencies.keys():
        add_sorted_data(workbook, frequencies[section], section)

    print('\tclosing the file')
    workbook.close()

corpus_sections = ['Amdo', 'Bodjong', 'Khabda', 'Khampa']
corpus_path = '../input/'
# processing the corpus
corpus_frequencies, corpus_total_frequency, corpus_origin, persons_frequencies, persons_total_frequency, persons_origin = processing_corpus(corpus_path)


# writing the individual xlsx
for person in persons_frequencies.keys():
    write_to_xlsx(person, persons_origin[person], persons_total_frequency[person], persons_frequencies[person])

# writing the main xlsx
write_to_xlsx('total', corpus_origin, corpus_total_frequency, corpus_frequencies)