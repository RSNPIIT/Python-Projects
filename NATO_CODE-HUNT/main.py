import pandas as pd

data = pd.read_csv("nato_phonetic_alphabet.csv")
phonetic_dict = {row.letter: row.code for (index, row) in data.iterrows()}
print(phonetic_dict)

def generate_phonetic():
    word = input("Enter a word: ").strip().upper()
    try:
        output_list = [phonetic_dict[l] for l in word]
    except KeyError :
        print("Only Letters Are Allowed")
        generate_phonetic()
    else:
        print(output_list)

generate_phonetic()

