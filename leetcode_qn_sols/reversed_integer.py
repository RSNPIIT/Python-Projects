# The Question is to Reverse an Integer and Return value as 0 if it crrosses the 2^31 threshold
import time as ti
import os as o
import sys as s

class Solution:
    def reverse(self, x: int) -> int:
        y_s = str(abs(x))
        rev = y_s[::-1]
        revi = int(rev)
        if x < 0:
            revi = (-1) * revi
        if revi < -1 * (2 ** 31) or revi > (2 ** 31) - 1:
            return 0
        return revi

try:
    x = abs(int(input("Enter the Number to reverse here :")))
except (KeyboardInterrupt , EOFError) as kb:
    print("Exitting...\nPlease Dont Spam")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    s.exit()
except ValueError as v:
    print("Wrong Value Given\nNot Allowed here")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    s.exit()
else:
    s1 = Solution(x)
    print(f"The Reverse of {x} is {s1.reverse()}")
finally:
    print("Another Leetcode Sollution Done")