import time as ti
import os as o

def clear_term():
    o.system('cls' if o.name == 'nt' else 'clear')

def start_timer(so):
    while so > 0:
        so_m = so // 60
        so_sec = so % 60
        if so_m < 10:
            so_m = f'0{so_m}'
        if so_sec < 10:
            so_sec = f'0{so_sec}'
        print(f" {so_m} : {so_sec} ")
        ti.sleep(1)
        so -= 1
    clear_term()

def user_inp():
    try:
        work_min = abs(int(input("Enter the Minutes You Wanna Work : "))) * 60
        break_min = abs(int(input("Enter the Break Minutes Here : "))) * 60
        cycl = abs(int(input("Enter How Many Cycles This will Happen : ")))
    except KeyboardInterrupt as intrp:
        print("\nExiting Code\n")
        exit()
    except ValueError as v:
        print("Wrong Value Given\nNot My Thang") 
        exit()
    for i in range(1 ,cycl + 1):
        print(f"ROUND : {i}\n")
        print("Working Time :- \n")
        start_timer(work_min)

        print("Break Time :- \n")
        start_timer(break_min)
    print("Timer Complete")

user_inp()