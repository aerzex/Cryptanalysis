import os
import sys
import re
import json

lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(lib_path)
from NgramAnalyze import chi_square_distribution, count_ngrams, count_ngrams_frequency, ALPHABET_RU, pretty_print_dict

# def main():
#     with open("Deshifrator\\sources\\2B.txt", "r", encoding="utf-8") as file:
#         text = file.read()
#     bigrams = count_ngrams(text, 3, ALPHABET_RU)
#     bigrams = {ngram : count for ngram, count in bigrams.items() if count != 0}
#     pretty_print_dict(bigrams, "test")
#     clean_text =list(re.sub(r'[^a-я]', '', text.lower()))
#     for i in range(len(clean_text)):
#         if clean_text[i:i+3] == "ьбу":
#             clean_text[i:i+3] = "тчк"
#         elif clean_text[i:i+3] == "сшь":
#             clean_text[i:i+3] == "зпт"
#     print(str(clean_text))


# if __name__ == "__main__":
#     main()

ENC_FILE_PATH = "SubstitutionCipherDecoder\\sources\\2B.txt"
DEC_FILE_PATH = "SubstitutionCipherDecoder\\sources\\test.txt"
SOLVED_LETTERS_PATH = "SubstitutionCipherDecoder\\sources\\decrypted_alphabet.json"


def main():
    with open(ENC_FILE_PATH, 'r', encoding='utf-8') as file:
        text = file.read()

    n = input("n: ")
    enc_freq = count_ngrams_frequency(text, n, ALPHABET_RU)

    filepath = f"NgramAnalyze\\sources\\normal_ngrams\\{n}_grams_frequency.json"
    with open(filepath, 'r', encoding='utf-8') as file:
        norm_freq = json.load(file)

    norm_freq = sorted(norm_freq.items(), key=lambda value: value[1], reverse=True )
    enc_freq = sorted(enc_freq.items(), key=lambda value: value[1], reverse=True )
    with open(SOLVED_LETTERS_PATH, 'r', encoding='utf-8') as file:
        solved = json.load(file)

    replace_table = {value: key for key, value in solved.items()}

    solved_text = list(text)
    for i in range(len(solved_text)):
        c = solved_text[i]
        if c in replace_table:
            solved_text[i] = replace_table[c]
        else:
            solved_text[i] = '_'

    solved_text = ''.join(solved_text)

    for i in range(min(len(norm_freq), len(enc_freq), 10)):
        print(
            f"[{norm_freq[i][0]:>10}]: {enc_freq[i][1]:.08f}  ->  [{enc_freq[i][0]:>10}]: {enc_freq[i][1]:.08f}"
        )

    print("\nПодстановки (расшифрование):")
    sorted_keys = sorted(replace_table.keys())
    print(' '.join(sorted_keys))
    sorted_values = [replace_table[k] for k in sorted_keys]
    print(' '.join(sorted_values))

    print("\nЗашифрованный текст:\n", text)
    print("\nРасшифрованный текст:\n", solved_text)

    with open(DEC_FILE_PATH, 'w', encoding='utf-8') as file:
        file.write(solved_text)

if __name__ == "__main__":
    main()