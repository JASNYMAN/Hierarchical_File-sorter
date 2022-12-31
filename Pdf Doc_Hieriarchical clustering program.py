import fitz
import os
import spacy
import shutil

print("Welcome to the PDF document heirarchical clustering program or P.D.H.C.P")
root = input("Please input the root directory, which contains all the unsorted pdf documents")
path_extract = str(root + "\\1.Extract")
path_spacy = str(root + "\\2.Spacy")
path_spacy_sort = str(root + "\\3.Sorted")
os.chdir(root)


# Section - Defines all functions
def folder_checkndcreate(folderpath):
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)


def doc_compare(doc1, doc2):
    similarity_index_words_unique_factor = 0.6
    similarity_index_words_frequency_factor = 1 - similarity_index_words_unique_factor

    doc1_words_freq_dic = {}
    doc2_words_freq_dic = {}
    similarity_index = 0
    similarity_index_words_frequency = 0

    with open(doc1, mode='r', encoding='utf8') as txt1:
        doc1_words_lst = txt1.read().split(' ')
        for word in doc1_words_lst:
            if word in doc1_words_freq_dic.keys():
                doc1_words_freq_dic[word] = doc1_words_freq_dic[word] + 1
            else:
                doc1_words_freq_dic[word] = 1

    with open(doc2, mode='r', encoding='utf8') as txt2:
        doc2_words_lst = txt2.read().split(' ')
        for word in doc2_words_lst:
            if word in doc2_words_freq_dic.keys():
                doc2_words_freq_dic[word] = doc2_words_freq_dic[word] + 1
            else:
                doc2_words_freq_dic[word] = 1

    set_A = set(doc1_words_freq_dic.keys())
    set_B = set(doc2_words_freq_dic.keys())
    set_C = set.intersection(set_A, set_B)
    set_Total = set_B.union(set_A)

    # Calculates similarity index for unique words
    similarity_index_words_unique = (len(set_C) / (len(set_Total))) * similarity_index_words_unique_factor

    # print("set A", set_A)
    # print("set B", set_B)
    # print("set C", set_C)
    # print("set T", set_Total)

    # Calculates the similarity between the two files in terms of shared words' frequency
    # creates a dictionary of all words that are in common, and an array for comparison
    freq_comparison_dic = {}
    for word in set_C:
        freq_comparison_dic[word] = []

    freq_proportion = 1 / len(set_C)

    for word, frequency in doc1_words_freq_dic.items():
        if word in set_C:
            freq_comparison_dic[word].append(int(frequency))

    for word, frequency in doc2_words_freq_dic.items():
        if word in set_C:
            freq_comparison_dic[word].append(int(frequency))

    for word, frequency in freq_comparison_dic.items():
        if frequency[0] == frequency[1]:
            similarity_index_words_frequency = similarity_index_words_frequency + freq_proportion
        else:
            pass
    print("\nComparing", doc1, "WITH\n", doc2)
    similarity_index_words_frequency = similarity_index_words_frequency * similarity_index_words_frequency_factor
    print('similarity_index_words_frequency', similarity_index_words_frequency)
    print('similarity_index_words_unique', similarity_index_words_unique)
    similarity_index = (similarity_index_words_unique + similarity_index_words_frequency)
    print('similarity index =', similarity_index)
    similarity_index = int(round((similarity_index_words_unique + similarity_index_words_frequency), 3) * 100)
    print('similarity index, adjusted =', similarity_index, "%")

    return similarity_index


# Finds the highest value in the array
# Iteratively finds the most similar values e.g. A and B, and compares their distances to other values,
# taking the highest distance between them.

# Based off the The UPGMA algorithm or the https://en.wikipedia.org/wiki/WPGMA
def binomial_clustering(y, node_length_array):
    # Creates an copied array of the previous array
    x = y.copy()
    # Finds the most similar values in the array
    while len(x) > 2:  # Sets the number of times this is going to repeat. Set until there are only 2 elements left

        highest_value = 100
        for r in range(1, len(x)):
            for c in range(1, len(x)):
                if x[r][c] != 0:
                    if x[r][c] < highest_value:
                        highest_value = x[r][c]
                        # Finds the row. column index for the lowest number, instead of the column, row index value.
                        if r < c:
                            lowest_row_1 = r
                            lowest_row_2 = c
                        else:
                            lowest_row_1 = c
                            lowest_row_2 = r
        # Calculates the node distance between the points
        node_length_array.append([[x[0][lowest_row_1], x[lowest_row_2][0]], highest_value / 2])

        # Combines the rows of the two closest items, picking the values with the shortest distance between them
        # (i.e.) highest value
        for column in range(1, len(x)):
            if int(x[lowest_row_1][column]) - int(x[lowest_row_2][column]) > 0:
                x[lowest_row_2][column] = 0
                x[column][lowest_row_2] = 0
            elif int(x[lowest_row_2][column]) - int(x[lowest_row_1][column]) > 0:
                x[lowest_row_1][column] = x[lowest_row_2][column]
                x[column][lowest_row_1] = x[lowest_row_2][column]
                x[lowest_row_2][column] = 0
            elif int(x[lowest_row_1][column]) - int(x[lowest_row_2][column]) == 0:
                x[lowest_row_2][column] = 0
            if int(x[lowest_row_1][column]) == int(highest_value):
                x[lowest_row_1][column] = 0

        # Renames the row according to the combination of the two
        combination = [x[0][lowest_row_1], x[0][lowest_row_2]]
        x[0][lowest_row_1] = combination
        x[lowest_row_1][0] = combination
        # Reduces the array by one row and one column
        del x[lowest_row_2]
        for row in range(0, len(x)):
            for column in range(1, len(x[row])):
                if column == lowest_row_2:
                    del x[row][column]
        print('-'.center(50, '-'))
        # Prints the array and the nodes
        for i in x:
            print(i)
        print("nodes :", node_length_array, '\n')
    return x[-1]


# Takes the output of Binomial clustering, and recusrively sorts the files into the correct heirarchical clustering
def doc_sorter(clust_outline, assig_letters, root_dir, old_dir):
    for i in clust_outline:
        # print(i, type(i))
        if type(i) == list:
            path = str(root_dir) + "\\" + str(i)
            folder_checkndcreate(path)
            doc_sorter(i, assig_letters, path, old_dir)
        elif type(i) == str:
            if i in assig_letters.keys():
                print(i, assig_letters[i])
                file = str(old_dir) + "\\" + str(assig_letters[i])
                shutil.move(file, root_dir)

# Appends the titles of the pdf documents to the pdf_list list
pdf_list = []
for i in os.listdir(root):
    if i[-4:len(i)] == ".pdf":
        pdf_list.append(i)

# Prints the list of pdf files in the root directory
print('\n')

for i in pdf_list:
    print(i)

# Creates a new folder to store the .txt extracted text from the pdf documents

folder_checkndcreate(path_extract)

# Opens the pdf documents, and stores contents in a .txt file
for pdf in pdf_list:
    # Loops through every pdf file in the directory
    doc = fitz.open(pdf)
    print('Processing', doc)  # Prints the document that the program is busy analysing.
    # Gets the number of pages of the pdf, and then loops through each page individually
    pages = len(doc)
    whole_doc = []  # list in which all processed blocks of extracted text is stored.
    # Loops through all the pages of the pdf, and extracts the blocks of text in that page, storing them in the whole doc list
    for page in range(pages):
        current_page = doc.load_page(page)
        text = current_page.get_text('text')
        text_spaceless = text.replace('\n', ' ').replace('\r', '')
        whole_doc.append(text_spaceless)  # Appends the data to the list
    whole_doc_str = "".join(whole_doc)  # Creates a string of the extracted text to be stored in the .txt file

    os.chdir(path_extract)
    text_file_name = str(pdf[0:-4]) + '.txt'
    # Writes the pdf text to the .txt file
    with open(text_file_name, mode='w', encoding='utf8') as txt:
        # writing to the .txt file
        pdf_title = pdf[0:-4]
        txt.write(whole_doc_str)
    os.chdir(root)

folder_checkndcreate(path_spacy)

# Processes all the extracted text documents, analyses them, and creates a new text document.
txt_extract_list = []
for i in os.listdir(path_extract):
    if i[-4:len(i)] == ".txt":
        txt_extract_list.append(i)

nlp = spacy.load('en_core_web_sm')
files_word_list = []

for txt_doc in txt_extract_list:
    os.chdir(path_extract)
    print("Processing", txt_doc)
    with open(txt_doc, mode='r', encoding='utf8') as file:
        file_text = file.read()
        doc = nlp(file_text)
    verb_list = []
    noun_list = []
    adj_list = []
    proper_noun_list = []
    for token in doc:
        if str(token.pos_) == "NOUN":
            noun_list.append(str(token.lemma_))
        elif str(token.pos_) == "ADJ":
            adj_list.append(str(token.lemma_))
        elif str(token.pos_) == "VERB":
            verb_list.append(str(token.lemma_))
        elif str(token.pos_) == "PROPN":
            proper_noun_list.append(str(token.lemma_))
    text_all = noun_list + verb_list + adj_list + proper_noun_list

    os.chdir(path_spacy)
    text_file_name = str(txt_doc[0:-4]) + '_spacy.txt'
    # Writes the pdf text to the .txt file
    with open(text_file_name, mode='w', encoding='utf8') as txt:
        # writing to the .txt file
        pdf_title = pdf[0:-4]
        txt.write(str(text_all))
    os.chdir(path_extract)

txt_spacied_list = []
for i in os.listdir(path_spacy):
    if i[-4:len(i)] == ".txt":
        txt_spacied_list.append(i)

# SECTION Assigns a letter of the alphabet to each document
# Extends the alphabet to include double letters to represent any documents that are greater than 26th on the list
AB = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q',
      'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
current_count = 0
passes = 0
for n in range(len(txt_spacied_list)):
    if current_count == 26:
        passes = passes + 1
        current_count = 0
    if n > 25:
        AB.append(str(AB[passes]) + str(AB[current_count]))
        current_count = current_count + 1
    else:
        pass
# Assigns an alphabetic code to each document
assignments = {}
letter_number = 0
for file in pdf_list:
    if file not in assignments.values():
        assignments[AB[letter_number]] = str(file)
        letter_number = letter_number + 1

for key, value in assignments.items():
    print(key, value)

# Section: This section creates an array to which all document comparisons will be added

# Creates an array of n size where n = len(AB)
comparisons_array = []
opening_line = [0]
for letter in AB:
    opening_line.append(letter)
comparisons_array.append(opening_line)
for letter in AB:
    comparisons_array.append([letter] + [0] * len(AB))

os.chdir(path_spacy)

# Creates a comparison for each file based on the words in the documents

row_number = 0
for txt_file_1 in txt_spacied_list:
    row_number = row_number + 1
    column_number = 1
    for txt_file_2 in txt_spacied_list:
        if row_number == column_number:
            comparisons_array[row_number][column_number] = 0
        elif comparisons_array[column_number][row_number] != 0:
            pass
        else:

            comparisons_array[row_number][column_number] = doc_compare(txt_file_1, txt_file_2)
        column_number = column_number + 1

for row in comparisons_array:
    print(row)

node_lengths = []

source = binomial_clustering(comparisons_array, node_lengths)
for i in node_lengths:
    print(i)
os.chdir(root)
with open('Document allocations.txt',mode='w',encoding='utf8') as text_file:
    for key, value in assignments.items():
        text_file.write('{} : {}'.format(key,value))
    for i in node_lengths:
        text_file.write(str(i))

doc_sorter(source, assignments, path_spacy_sort, root)

print('SUCCESS!')

