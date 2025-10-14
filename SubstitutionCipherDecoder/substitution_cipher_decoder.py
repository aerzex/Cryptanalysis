import os
import sys
import re
import json
from itertools import product

lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(lib_path)
from NgramAnalyze import count_ngrams, ALPHABET_RU, pretty_print_dict

ENC_FILE_PATH = "SubstitutionCipherDecoder\\sources\\2B.txt"
DEC_FILE_PATH = "SubstitutionCipherDecoder\\sources\\test.txt"
SOLVED_LETTERS_PATH = "SubstitutionCipherDecoder\\sources\\decrypted_alphabet.json"


def print_count_ngrams(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        text = file.read()
    n = int(input("n: "))
    treshold = int(input("Enter minimum threshold for display: "))
    ngrams = count_ngrams(text, n, ALPHABET_RU)
    filtered_ngrams = {ngram: value for ngram, value in ngrams.items() if value >= treshold}
    sorted_ngrams = dict(sorted(filtered_ngrams.items(), key=lambda value: value[1], reverse=True))
    pretty_print_dict(sorted_ngrams, f"{n}-grams (count)")

def load_mapping():
    filepath = input(f"Enter file path for mapping (Enter for {SOLVED_LETTERS_PATH})") or SOLVED_LETTERS_PATH
    with open(filepath, 'r', encoding='utf-8') as file:
        solved = json.load(file)
    pretty_print_dict(solved, "solved alphabet")

def make_substitution(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        solved = json.load(file)
    print("=== Substitution Edit Mode ===")
    print("Format: a -> n")
    print("Commands: save — save and exit, exit — quit without saving, del X — delete a mapping")
    print("Current mappings:")
    for k, v in sorted(solved.items()):
        print(f"  {k} -> {v[0]}")
    print("-----------------------------------------")

    while True:
        user_input = input("> ").strip().lower()

        if user_input in {"exit"}:
            print("Exit without saving.")
            break

        if user_input in {"save"}:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(solved, f, ensure_ascii=False, indent=2)
            print(f"Saved to {filepath}")
            break

        if user_input.startswith("del "):
            key = user_input[4:].strip()
            if key in solved:
                del solved[key][0]
                print(f"Deleted mapping for '{key}'.")
            else:
                print(f"No mapping found for '{key}'.")
            continue

        if "->" in user_input:
            parts = [p.strip() for p in user_input.split("->")]
            if len(parts) == 2 and len(parts[0]) == 1 and len(parts[1]) == 1:
                src, dst = parts
                solved[src][0] = dst
                solved[src][1] = dst
                print(f"Added: {src} -> {dst}")
            else:
                print("Invalid format. Use: a -> n")
        else:
            print("Invalid input. Use format 'a -> n' or commands: save, exit, del X")   


def initiate_solved_dict(filepath: str=SOLVED_LETTERS_PATH, alphabet: str=ALPHABET_RU):
    if not os.path.exists(filepath):
        solved = {ch: [ch, "_"] for ch in alphabet}
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(solved, f, ensure_ascii=False, indent=2)

def text_compare(enc_filepath, solved_filepath):
    with open(enc_filepath, 'r', encoding='utf-8') as file:
        enc_text = file.read()

    if not os.path.exists(solved_filepath):
        print(f"Error: substitution file '{solved_filepath}' not found.")
        return

    with open(solved_filepath, 'r', encoding='utf-8') as file:
        try:
            solved = json.load(file)
            if not isinstance(solved, dict):
                print("Error: substitution file does not contain a valid dictionary.")
                return
        except json.JSONDecodeError:
            print("Error: failed to parse substitution JSON file.")
            return
        
    enc_lines = [line.strip() for line in enc_text.splitlines() if line.strip()]
    print("=== Decrypted text (left) vs Masked (right) ===\n")
    for line in enc_lines:
        decrypted_line = []
        masked_line = []

        for c in line.lower():
            if c in solved:
                decrypted_line.append(solved[c][0])
                masked_line.append(solved[c][1])
            else:
                decrypted_line.append(c)
                masked_line.append(c if c == ' ' else "_")

        print(''.join(decrypted_line))
        print(''.join(masked_line))
        print()

    print("===============================================")        

def print_encrypted_text(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        text = file.read()
    print("=== Encrypted Text ===")
    print(text.lower())
    print("======================")
    return text

def print_decrypted_text(enc_filepath, solved_filepath):
    with open(enc_filepath, 'r', encoding='utf-8') as file:
        enc_text = file.read()

    if not os.path.exists(solved_filepath):
        print(f"Error: substitution file '{solved_filepath}' not found.")
        return

    with open(solved_filepath, 'r', encoding='utf-8') as file:
        try:
            solved = json.load(file)
            if not isinstance(solved, dict):
                print("Error: substitution file does not contain a valid dictionary.")
                return
        except json.JSONDecodeError:
            print("Error: failed to parse substitution JSON file.")
            return
        
    decrypted_chars = []
    clean_text = re.sub(r'[^' + ALPHABET_RU + r']', '', enc_text.lower())
    for char in clean_text:
        decrypted_chars.append(solved.get(char, '_')[0])
    
    text = ''.join(decrypted_chars)
    print(text)

def main():
    enc_filepath = input(f"Enter path to encrypted file (Enter for {ENC_FILE_PATH}:) ") or ENC_FILE_PATH
    map_filepath = input(f"Enter file path for mapping (Enter for {SOLVED_LETTERS_PATH})") or SOLVED_LETTERS_PATH
    initiate_solved_dict(map_filepath)
    while True:
        print("\n╭──────────────────────────────────────────────╮")
        print("│ Menu:                                        │")
        print("│ 1. Calculate n-grams for text                │")
        print("│ 2. Make a substitution                       │")
        print("│ 3. Show mapping                              │")        
        print("│ 4. Show encrypted text                       │")
        print("│ 5. Show text compare                         │")
        print("│ 6. Show decrypted text                       │")
        print("│ 7. Exit                                      │")
        print("╰──────────────────────────────────────────────╯")
        choice = input("Select an option: ")
        if choice == '1':
            print_count_ngrams(enc_filepath)
        elif choice == '2':
            make_substitution(map_filepath)
        elif choice == '3':
            load_mapping()
        elif choice == '4':
            print_encrypted_text(enc_filepath)
        elif choice == '5':
            text_compare(enc_filepath, map_filepath)
        elif choice == '6':
            print_decrypted_text(enc_filepath, map_filepath)
        elif choice == '7':
            break
        else:
            print("Invalid choice.")
    

    

if __name__ == "__main__":
    main()