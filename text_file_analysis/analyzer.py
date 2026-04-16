import prettytable as prt
import time as ti
import os as o
import platform as pt
import sys as s

# Static File
FILE = 'sample_file.txt'
MODE = 'w'
SYM = '-'*50

# Extracting the Raw Txt Data
try:
    with open(FILE) as r:
        k = r.readlines()
except FileNotFoundError as f:
    print(f"The File is Not Found\nMaking the file\n")
    ti.sleep(1)
    with open(FILE , MODE) as r:
        pass
    o.system('cls' if pt.system() == 'windows' else 'clear')
    s.exit()

else:
    #  Making the text as a complete dictionary form if the text part is not empty
    if k is not None:
        stdns = []
        for l in k[ 1: ]:
            parts = l.split()

            name = parts[0]
            roll = int(parts[1])
            age = int(parts[2])

            marks = list(map(int , parts[3:]))         

            stud = {
                'name' : name,
                'roll' : roll,
                'age' : age,
                'marks' : marks
            }

            stdns.append(stud)

        #  Displaying the Records in an easy to undertsand manner
        table = prt.PrettyTable()
        table.field_names = ['Name' , 'RollNo.' , 'Age' , 'Marks']
        for stu in stdns:
            table.add_row([
                stu['name'],
                stu['roll'],
                stu['age'],
                sum(stu['marks'])
            ])

        print(f"{SYM}\nThe Records are as follows are as follows :-\n\n{table}\n{SYM}")

        # Extracting the Maximum Student His/Her Age and Roll Number based on sum of marks and the class marks' sum average
        max_mar = 0
        tot_sum = 0
        max_st = None
        std_cnt = 0
        for x in stdns:
            mar = sum(x['marks'])
            tot_sum += mar
            std_cnt += 1
            if mar > max_mar:
                max_mar = mar
                max_st = x
            else:
                continue
        
        std_avg = round( tot_sum / std_cnt , 3)
        print(f"\n\n{SYM}\nPython's Analysis :-\nClass' Average -> {std_avg}\nTopper's Name -> {max_st['name']}\nAge -> {max_st['age']}\nRoll Number -> {max_st['roll']}\nMarks -> {sum(max_st['marks'])}\n{SYM}")
    else:
        print("The File is Empty\nPlease Add something inside of it")
        ti.sleep(1)
        o.system('cls' if pt.system() == 'windows' else 'clear')
        s.exit()

finally:
    print(f"{SYM}\n\n🄯 RSNPIIT (Ramrup Satpati) IIT Madras\nReleased under the GNU GPLv3 and later license\n")