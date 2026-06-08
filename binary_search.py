import time as ti
import sys as s
import os as o

# Static Elements 
SYM = '-' * 50

# The binary function essentially goes here
def binary_search(arr ,x):
    left = 0
    right = len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == x:
            return mid
        elif x > arr[mid]:
            left = mid + 1
        else:
            right = mid - 1
    return -1

# Asking in for user input
try:
    n = abs(int(input("Enter the number of the elements in the list -> ")))
    li = []
    for i in range(n):
        while True:
            print(SYM)
            try:
                el = int(input(f"Enter the element at position {i + 1} here :-> "))        
                li.append(el) 
                break   
            except (KeyboardInterrupt , EOFError) as kb:
                print("\nIllegal Exit detected ...\nNot Allowed")
                continue
            except ValueError as vl:
                print("Non Integer values not allowed\n")
                continue

    try:
        val = int(input("Enter the value of the element you wanna search here -> "))
    except (KeyboardInterrupt , EOFError) as kb:
        print("\nIllegal Exit detected ...\nNot Allowed")
        pass
    except ValueError as vl:
        print("Non Integer values not allowed\n")
        ti.sleep(1)
        o.system('cls' if o.name == 'nt' else 'clear')
        s.exit()
    li = list(set(li)).sort()
    oit = binary_search(li , val)
    if oit != -1:
        print(f"The Element {val} is found in the list at position {oit}\nThis is a success")
    else:
        print(f"The Element {val} is not found in the list anywhwere")
except (KeyboardInterrupt , EOFError) as kb:
    print("\nExit detected ...\nExiting")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    s.exit()
except ValueError as vl:
    print("Non Integer values not allowed\n")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    s.exit()
finally:
    print(SYM)
