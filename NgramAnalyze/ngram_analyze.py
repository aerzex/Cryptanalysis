import json
from itertools import product
import re
from scipy import stats
import shutil

ALPHABET_EN = "abcdefghijklmnopqrstuvwxyz"
ALPHABET_RU = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
DEFAULT_TEXT_PATH = "NgramAnalyze\\sources\\war_and_peace.ru.txt"
DEFAULT_ENC_PATH = "NgramAnalyze\\sources\\war_and_peace_encrypted.txt"
DEFAULT_NORM_NGRAMS_PATH = "NgramAnalyze\\sources\\normal_ngrams"
DEFAULT_ENC_NGRAMS_PATH = "NgramAnalyze\\sources\\ngrams"

def generate_ngram_dict(n: int, alphabet: str):
    combinations = (''.join(comb) for comb in product(alphabet, repeat=n))
    ngram_dict = {combination: 0 for combination in combinations}
    return ngram_dict

def count_ngrams_frequency(text: str, n: int, alphabet: str):
    clean_text = re.sub(r'[^' + re.escape(alphabet) + r']', '', text.lower())
    ngrams = count_ngrams(clean_text, n, alphabet)
    N = sum(ngrams.values())
    ngram_frequency = {ngram: (count / N) for ngram, count in ngrams.items()} if N > 0 else {}
    return ngram_frequency

def vigenere_encrypt(text: str, filepath: str, key: str, alphabet: str):
    clean_text = re.sub(r'[^' + re.escape(alphabet) + r']', '', text.lower())
    encrypted = []
    for i, char in enumerate(clean_text):
        char_indx = (alphabet.index(char) + alphabet.index(key[i % len(key)])) % len(alphabet)
        encrypted.append(alphabet[char_indx])
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(''.join(encrypted))
    return ''.join(encrypted)

def count_ngrams(text: str, n: int, alphabet: str):
    text = text.lower()
    clean_text = re.sub(r'[^' + re.escape(alphabet) + r']', '', text)
    if n < 4:   
        ngrams = generate_ngram_dict(n, alphabet)
    else:
        ngrams = {}
    for i in range(len(clean_text) - n + 1):
        ngram = clean_text[i:i+n]
        ngrams[ngram] = ngrams.get(ngram, 0) + 1
    return ngrams 

def save_ngrams(ngrams: dict, filepath: str):
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(ngrams, file, ensure_ascii=False, indent=4) 

def open_ngrams(filepath: str):
    with open(filepath, "r", encoding="utf-8") as file:
        ngrams = json.load(file)
    return ngrams

def chi_square_distribution(enc_ngram: dict, nrm_ngram_fr: dict, n: int):
    N_enc = sum(enc_ngram.values())
    chi2_critical = stats.chi2.ppf(0.95, (33**n) - 1)
    chi2 = 0.0
    for ngram, count in nrm_ngram_fr.items():
        if count != 0:
            chi2 += ((enc_ngram.get(ngram, 0.0) - N_enc * count)**2 / (N_enc * count))
        else:
            continue

    return chi2, chi2_critical

def pretty_print_dict(dictionary: dict, title: str, is_freq: bool = False):
    terminal_width = shutil.get_terminal_size().columns
    items = list(dictionary.items())

    print(f"\n╭─{'─' * len(title)}─╮")
    print(f"│ {title} │")
    print(f"╰─{'─' * len(title)}─╯\n")

    max_item_length = max(len(f"{ng}: {val * 100:.6f}%" if is_freq else f"{ng}: {val}") for ng, val in items) + 2
    items_per_row = max(1, (terminal_width - 2) // (max_item_length + 2))

    for i in range(0, len(items), items_per_row):
        row_items = items[i:i + items_per_row]
        row = "  " 
        for ng, val in row_items:
            item_str = f"{ng}: {val * 100:.6f}%" if is_freq else f"{ng}: {val}"
            row += item_str.ljust(max_item_length) + "  "
        print(row.rstrip())
    print()

def print_count_ngrams():
    filepath = input(f"Enter file path (Enter for {DEFAULT_TEXT_PATH}): ") or DEFAULT_TEXT_PATH
    n = int(input("Enter n: "))
    threshold = float(input("Enter minimum threshold for display: "))
    with open(filepath, "r", encoding="utf-8") as file:
        text = file.read()
    ngrams = count_ngrams(text, n, ALPHABET_RU)
    filtered_ngrams = {ngram: value for ngram, value in ngrams.items() if value >= threshold}
    sorted_ngrams = dict(sorted(filtered_ngrams.items(), key=lambda value: value[1], reverse=True))
    pretty_print_dict(sorted_ngrams, f"{n}-grams (count)")

def print_count_ngrams_frequency():
    filepath = input(f"Enter file path (Enter for {DEFAULT_TEXT_PATH}): ") or DEFAULT_TEXT_PATH
    with open(filepath, "r", encoding="utf-8") as file:
        text = file.read()
    # filepath1 = "NgramAnalyze\\sources\\war_and_peace.ru.txt"
    # with open(filepath1, "r", encoding="utf-8") as file:
    #     text1 = file.read()
    # filepath2 = "NgramAnalyze\\sources\\crime_and_punishment.ru.txt"
    # with open(filepath2, "r", encoding="utf-8") as file:
    #     text2 = file.read()
    # filepath3 = "NgramAnalyze\\sources\\anna_korenina.ru.txt"
    # with open(filepath3, "r", encoding="utf-8") as file:
    #     text3 = file.read()
    n = int(input("Enter n: "))
    threshold = float(input("Enter minimum threshold for display (in %): "))
    freq = count_ngrams_frequency(text, n, ALPHABET_RU)
    save_ngrams(freq, f"NgramAnalyze\\sources\\normal_ngrams\\{n}_grams_frequency.json")
    filtered_ngrams = {ngram: value for ngram, value in freq.items() if value * 100 >= threshold}
    sorted_ngrams = dict(sorted(filtered_ngrams.items(), key=lambda x: x[1], reverse=True))
    pretty_print_dict(sorted_ngrams, f"{n}-grams (frequency)", is_freq=True)

def print_chi_square_distribution():
    dirpath_normal = input(f"Enter directory path to normal json file (Enter for {DEFAULT_NORM_NGRAMS_PATH}): ") or DEFAULT_NORM_NGRAMS_PATH
    filepath_enc = input(f"Enter file path to encrypted file (Enter for {DEFAULT_ENC_PATH}): ") or DEFAULT_ENC_PATH
    n = int(input("Enter n: "))
    with open(filepath_enc, "r", encoding="utf-8") as file:
        text = file.read()
    norm_ngrams_freq = open_ngrams(dirpath_normal + f"\\{n}_grams_frequency.json")
    enc_ngrams = count_ngrams(text, n, ALPHABET_RU)
    chi2, critical= chi_square_distribution(enc_ngrams, norm_ngrams_freq, n)
    print("\n╭────────────────────────────────────────────────╮")
    print(f"│ Chi-squared: {chi2:15.2f}                   │")
    print(f"│ Critical value (95%): {critical:14.2f}           │")
    print("╰────────────────────────────────────────────────╯")


def main():
    
    while True:
        print("\n╭──────────────────────────────────────────────╮")
        print("│ Menu:                                        │")
        print("│ 1. Calculate n-grams for text                │")
        print("│ 2. Calculate n-gram frequency for text       │")
        print("│ 3. Calculate chi-squared                     │")
        print("│ 4. Exit                                      │")
        print("╰──────────────────────────────────────────────╯")
        choice = input("Select an option: ")
        if choice == '1':
            print_count_ngrams()
        elif choice == '2':
            print_count_ngrams_frequency()
        elif choice == '3':
            print_chi_square_distribution()
        elif choice == '4':
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()