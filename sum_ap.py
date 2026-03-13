import time as ti
import os as o

print("\nWelcome to GP Square Game Proj")
try:
    n = abs(int(input("Enter the Value upto which youre gonna sum : ")))
except (KeyboardInterrupt , EOFError) as kb:
    print("Exitting Please dont spam Here\n")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    exit()
except ValueError as v:
    print("\nNon Integral Values Given\nNot Allowed here\n")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    exit()
else:
    sum = 0
    for i in range(1 , n+1):
        sum += i**2

    print(f"The Final G.P. sum is : {sum}") 
finally:
    print("The G.P. Goes ---")