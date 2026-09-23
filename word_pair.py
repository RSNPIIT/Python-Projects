import sys as s
import time as ti
import os as o

try:
    n = abs(int(input("Enter the number of sentences you wanna get a pair of :-> ")))

except ValueError as v:
    print("Error Happened here\nPlease retry")
    o.system("cls" if o.name == 'nt' else "clear")
    ti.sleep(3)
    s.exit()

else:
    SLIST = []
    WLIST = set()

    for i in range(n):
        sent = input(f"Enter the sentence number {i+1} here :-> ").strip().lower()
        SLIST.append(sent)

    for sente in SLIST:
        words = sente.split()

        for i in range(len(words) - 1):
            pair = (words[i], words[i+1])
            WLIST.add(pair)

    ti.sleep(2)
    print(f"The Word Pairs formed here are -> {len(WLIST)}")

finally:
    print("Copyleft | Ramrup Satpati | 2026 | IIT Madras | Released under the GNU GPLv3 license")