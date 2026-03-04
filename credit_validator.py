import os as o

sum_odd = 0
sum_ev = 0
total = 0

card_numb = input("Enter your Credit Card Number : ")
card_numb = card_numb.replace('-','')
card_numb = card_numb.replace(' ','')
card_numb = card_numb[::-1]

for x in card_numb[::2]:
    sum_odd += int(x)

for x in card_numb[::2]:
    x = int(x) * 2
    if x > 9:
        sum_ev += (x % 10) + 1
    else:
        sum_ev += x

total = sum_odd + sum_ev
if total % 10 == 0:
    o.system('cls' if o.name == 'nt' else 'clear')
    print(f"The Number {card_numb} is Valid !")

else:
    o.system('cls' if o.name == 'nt' else 'clear')
    print(f"The Number {card_numb} is Invalid !")

