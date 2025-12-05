import pandas as pd

data = pd.read_csv("nato_phonetic_alphabet.csv")
print('The NATO Code For your sake is : \n')
phonetic_dict = {row.letter: row.code for (index, row) in data.iterrows()}
print(phonetic_dict)

def generate_phonetic():
    word = input("Enter a word: ").strip().upper()
    try:
        output_list = [phonetic_dict[l] for l in word]
    except KeyError :
        print("Only Letters Are Allowed\n")
        generate_phonetic()
    else:
        print("The NATO Alphabet Encryption of your Word is :-\n")
        for i in output_list:
            print(i , end = ' ')

generate_phonetic()
