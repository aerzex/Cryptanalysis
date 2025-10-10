import sys
import os
import json
import re

lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(lib_path)
from NgramAnalyze import chi_square_distribution, count_ngrams_frequency, save_ngrams, open_ngrams

ALPHABET_RU = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя_"
ENC_FILE_PATH = "PermutationCipherDecoder\\sources\\9.15"
DEFAULT_NORM_BIGRAMS_PATH = "NgramAnalyze\\sources\\normal_ngrams\\2_grams_frequency.json"


def find_column_order(matrix):
    columns = len(matrix)
    links = [0] * columns
    for i in range(columns):
        for j in range(columns):
            if matrix[i][j] == 1:
                links[j] += 1
    
    start = links.index(0)
    
    order = [start]
    current = start
    visited = set([start])
    
    while len(order) < columns:
        for next_col in range(columns):
            if matrix[current][next_col] == 1 and next_col not in visited:
                order.append(next_col)
                visited.add(next_col)
                current = next_col
                break
    
    return order


def find_adjacency_matrix(enc_text_matrix: list, rows: int, columns: int, norm_freq: dict):
    matrix = [[0 for j in range(columns)] for i in range(columns)]

    for i in range(columns):
        chi2_dict = {}
        for j in range(columns):
            if i == j:
                continue
            
            bigrams = {}
            for k in range(rows):
                left = enc_text_matrix[k][i]
                right = enc_text_matrix[k][j]
                bigrams[left + right] = bigrams.get(left + right, 0) + 1

            chi2_dict[j] = chi_square_distribution(bigrams, norm_freq, 2)[0]
        min_chi2 = min(chi2_dict.values())
        for j, chi2 in chi2_dict.items():
            if chi2 == min_chi2:
                matrix[i][j] = 1
    
    return matrix

def main():
    # with  open("PermutationCipherDecoder\\sources\\war_and_peace.ru.txt", "r", encoding="utf-8") as file:
    #     wap = file.read()

    # n_f = count_ngrams_frequency(wap, 2, ALPHABET_RU)
    # save_ngrams(n_f, "PermutationCipherDecoder\\sources\\normal_ngrams\\2_grams_frequency.json")
    norm_freq = open_ngrams("PermutationCipherDecoder\\sources\\normal_ngrams\\2_grams_frequency.json")

    with open(ENC_FILE_PATH, "r", encoding="cp866") as file:
        lines = file.readlines()  

    lines = [re.sub(r'[^' + ALPHABET_RU + r']', '', line.lower()).strip() for line in lines]

    enc_text_matrix = [list(line.strip()) for line in lines]

    rows = len(enc_text_matrix)
    columns = len(enc_text_matrix[0]) if rows > 0 else 0

    matrix = find_adjacency_matrix(enc_text_matrix, rows, columns, norm_freq)
    
    for i in range(len(matrix)):
        print(matrix[i])

    column_order = find_column_order(matrix)
    print("Columns order:", column_order)
    
    decrypted_matrix = [[enc_text_matrix[i][j] for j in column_order] for i in range(rows)]
    decrypted_text = ''.join(''.join(row) for row in decrypted_matrix)
    
    print("Decoded text:")
    print(decrypted_text)

    
    

if __name__ == "__main__":
    main()