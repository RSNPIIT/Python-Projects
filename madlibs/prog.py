import time as ti
FILE = 'story.txt'

with open('story.txt') as j:
    stry = j.read()

NFILE = 'correct.txt'

print(f"The Story is : \n{stry}\n")

#Static Variables
wrds = set()
str_of_wrd = -1

str_th = '<'
end_th = '>'

for i, char in enumerate(stry):
    if char == str_th:
        str_of_wrd = i

    if char == end_th and str_of_wrd != -1:
        wrd = stry[str_of_wrd : i + 1]
        wrds.add(wrd)
        str_of_wrd = -1

print(f"The Unique Placeholder are :-\n{wrds}\n")

answ = {}

for x in wrds:
    ans = input(f"\nEnter a word for {x} : ").strip().title()
    answ[x] = ans

print(f'Your Answers are : \n{answ}')

for x in wrds:
    stry = stry.replace(x ,answ[x])

print(f'\nThe Final Story is \n\n{stry}\n')

print("\n|||||Writing to File ....")
with open(NFILE , 'w') as d:
    d.write(stry)

ti.sleep(1)
print('\nDone')