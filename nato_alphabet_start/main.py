# student_dict = {
#     "student": ["Angela", "James", "Lily"], 
#     "score": [56, 76, 98]
# }

#Looping through dictionaries:
# for (key, value) in student_dict.items():
#     Access key and value
#     pass
print("Welcome to Ramrup's (RSNPIIT) NATO Language Converter \nCopyLeft Tux Technologies ")

import pandas as pd
val = pd.read_csv('nato_phonetic_alphabet.csv')
dic = val.to_dict()
# print(dic)

#Loop through rows of a data frame
#TODO 1. Create a dictionary in this format:
# {"A": "Alfa", "B": "Bravo"}
#We access the elements by a dot(.)
# Syntax :-> {new_key:new_value for (index, row) in df.iterrows()}
xal = {row.letter : row.code for (index, row) in val.iterrows()}

print('The Standard Nato Coded Cipher Chosen For Clarity is : \n')
print(f'{xal}\n')

#Access index and row
#Access row.student or row.score
# pass

# Keyword Method with iterrows()
#TODO 2. Create a list of the phonetic code words from a word that the user inputs

u_in = input('Enter a word here : ').strip().upper()
lis = [xal[l] for l in u_in]
print('The Nato Code is : \n')

for i in lis:
    print(i ,end = ' ')

