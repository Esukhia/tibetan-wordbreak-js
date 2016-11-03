# tibetan-wordbreak-js

This repository is work in progress, use at your own risk!

Download cutWords.html and open it locally.

ཞུས་དག་དང་མིང་ཚིག་བཏུབ་པའི་སྙེ་ཆས་ཐད་ཀར་འབད་སྤྱོད་གནང་བ་ལ་cutWords.htmlཞེས་པ་ཕབ་ལེན་གནང་ནས་དྲ་ཚིག་སྙེ་ཆས་གང་རུང་གིས་ཕྱེད་དགོས། 


InDesignནང་འབད་སྤྱོད་གནང་བར་cutWords.jsཞེས་པ་ཕབ་ལེན་གནང་ནས་སྙེ་ཆས་དེའི་ནང་གི་scriptགི་ཡིག་སྣོད་དུ་བཅུག་དགོས།

Step 1 : 
    fill the make/updateLexicon/input folder with the new files
    run new_lexicon.py
    result : 
        - ./output/all_entries<>.txt file (the complete lexicon at this stage)
        - make/updateJs/src/new_entries/oral_corpus_<>.txt (the newly added words)
Step 2:
    run make_cut_words.py to generate the segmenting html file

Step 2:
    run /make/updateLexicon/oral_corpus/stats.py
    result:
        - list of xlsx files for every employee and a total file for the team manager

Note :
    The input folder must only contain new files, as everything in there will be counted for the new words.
    Once the files have been processed, put them in the oral_corpus/corpus_files folder for archiving.