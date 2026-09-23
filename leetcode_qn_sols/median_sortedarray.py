# The Question is to basically find the Median of two sorted lists
import time as ti
import random as r
import sys as s
import os as o

class Solution:
    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
        lst3 = nums1 + nums2
        lst3.sort()
        med_val = 0
        if len(lst3) % 2 != 0:
            med_val = float(lst3[len(lst3) // 2])
        else:
            one_val = float(lst3[len(lst3) // 2])
            sec_val = float(lst3[(len(lst3) // 2) - 1])
            med_val = (one_val + sec_val) / 2
        return med_val
    
try:
    n1 = abs(int(input("Enter a range upto which ideally the first list should stretch : ")))
    n2 = abs(int(input("Enter a range upto which ideally the second list should stretch : ")))
except (KeyboardInterrupt , EOFError):
    print("Exitting....\nPlease dont spam")
    ti.sleep()
    o.system('cls' if o.name == 'nt' else 'clear')
    s.exit()
except ValueError as v:
    print("Non Integral Values aren't allowed here\nThese should not be given")
    ti.sleep()
    o.system('cls' if o.name == 'nt' else 'clear')
    s.exit()
else:
    if n1 >= 100 or n2 >= 100:
        print("These Values are too long and will take a lot of time and waste (potentially) lots of resources..\nSo for Safety reasons we have capped the lists at 99 max\n")
        ti.sleep()
        o.system('cls' if o.name == 'nt' else 'clear')
        s.exit()
    elif n1 in [0 ,1] and n2 in [0 ,1]:
        print("This Wont Do...\nWhy you ask\nWell its too short so.. Please (Re)enter")
        ti.sleep()
        o.system('cls' if o.name == 'nt' else 'clear')
        s.exit()
    a = r.randint(1 ,n1)
    b = r.randint(2 ,n2)

    if a != 1 or b != 1:
        lis1 = [i for i in range(1 , a)]
        lis2 = [j for j in range(1 , b)]
        s_cl = Solution(lis1 , lis2)
        print(f"The Median of Arrays {lis1} and {lis2} are :- {s_cl.findMedianSortedArrays}")
    else:
        print("Please Re-Enter Cause You Yourself think--\nYou Making a List and the loop is from 1 to 1\nThus for safety reasons 1 is not allowed here")
        ti.sleep()
        o.system('cls' if o.name == 'nt' else 'clear')
        s.exit()
finally:
    print("This is my sollution of problem on Leetcode\nNOTE - Please going through the code do not judge as I am a beginner in the Comp.Coding world\nAlthough this may not be the most optimal , it works !! and thats what mattter most as a beginner")