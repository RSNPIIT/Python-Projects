attmpt = 0

nato_alph = {
    'A': 'Alfa',
    'B': 'Bravo',
    'C': 'Charlie',
    'D': 'Delta',
    'E': 'Echo',
    'F': 'Foxtrot',
    'G': 'Golf',
    'H': 'Hotel',
    'I': 'India',
    'J': 'Juliett',
    'K': 'Kilo',
    'L': 'Lima',
    'M': 'Mike',
    'N': 'November',
    'O': 'Oscar',
    'P': 'Papa',
    'Q': 'Quebec',
    'R': 'Romeo',
    'S': 'Sierra',
    'T': 'Tango',
    'U': 'Uniform',
    'V': 'Victor',
    'W': 'Whiskey',
    'X': 'X-ray',
    'Y': 'Yankee',
    'Z': 'Zulu'
}


soviet_digits = {
    '0': 'ноль',
    '1': 'один',
    '2': 'два',
    '3': 'три',
    '4': 'четыре',
    '5': 'пять',
    '6': 'шесть',
    '7': 'семь',
    '8': 'восемь',
    '9': 'девять'
}

while True:
    said_name = []
    attmpt += 1

    print('Welcome to NATO (OTAN) Language Phonetic Converter by Ramrup Satpati // RSNPIIT \n(ↄ) NATO inc.\n')

    ch = input('Enter Your Message  Here :-> ').strip().upper()
    for i in ch:
        if i in nato_alph:
            said_name.append(nato_alph[i])
        elif i in soviet_digits :
            said_name.append(soviet_digits[i])

    print('Your Phonetic Message is -> \n')
    for s in said_name:
        print(s , end = ' ')
    print('\n')

    oi = input('Comrade do you wanna continue -> Enter a Y or an N : ').strip().lower()
    if oi == 'y':
        continue
    elif oi == 'n':
        print(f'Goodbye \nApp used for {attmpt} times')
        break
    else:
        print('Wrong Choice \nDefaulting to Yes ')
        print('Default Successful\n')
        continue
