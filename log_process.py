import datetime as dt
import time as ti
import os as o
import sys as s
import platform as pt
import pprint as pp

# Making a Log Processor using the Power of Python
def process_logs(log_date , *logs , min_length = 10):
    count = 0
    d = {
        'invalid' : [],
        'critical' : [],
        'normal' : [],
        'metadata' : {}
    }

    #Looping through the Arguments Given
    for i in logs:
        clear_log = i.strip(" ").lower()

        if len(clear_log) < min_length:
            d['invalid'].append(clear_log)

        elif 'admin' in clear_log or 'password' in clear_log or 'root' in clear_log:
            d['critical'].append(clear_log)

        else:
            d['normal'].append(clear_log)
        
        count += 1

    d['metadata']['date'] = log_date
    d['metadata']['total-processed'] = count

    return d

# Now We call our function here
now = dt.datetime.now()
yr = now.year
mon = now.month
dai = now.day

if mon < 10:
    mon = f'0{mon}'

if dai < 10:
    dai = f'0{dai}'

date = f'{dai}-{mon}-{yr}'

try:
    mini = int(input("Enter the Minimum Length Here : "))

    if mini <= 0:
        print("Not Allowed to use it here\nDefaulting the min argument to a safe integer\n")
        mini = 10

except (KeyboardInterrupt , EOFError) as kb:
    print("Skipping Iteration Please don't Spam Ctrl-C\n")
    ti.sleep(1)
    o.system('cls' if pt.system() == 'windows' else 'clear')
    s.exit()

except ValueError as v:
    print(f"Non Integer Value Given\nThese are not allowed over here\n")
    ti.sleep(1)
    o.system('cls' if pt.system() == 'windows' else 'clear')
    s.exit()

except OverflowError as ov:
    print("OverFlow Error Occurred Here\n")
    ti.sleep(1)
    o.system('cls' if pt.system() == 'windows' else 'clear')
    s.exit()

except Exception as e:
    print(f"Some Exception occurred here\n")
    ti.sleep(1)
    o.system('cls' if pt.system() == 'windows' else 'clear')
    s.exit()

else:
    print("Enter Your Logs\nEnter Done when finished ->\n")
    user_log = []
    while True:
        log = input()
        if log.lower() == 'done':
            break
        else:
            user_log.append(log)
            continue

    res = process_logs(date , *user_log , min_length = mini)
    print("The Status Result is :-\n")
    pp.pprint(res)

finally:
    print("🄯 RSNPIIT (Ramrup Satpati) -- IIT Madras\nReleased Under the GNU GPLv3 license")