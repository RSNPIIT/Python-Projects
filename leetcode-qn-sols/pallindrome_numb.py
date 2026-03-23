import time as ti
import sys as s
import os as o

class Solution:
    def __init__(self , x):
        self.x = x

    def isPalindrome(self):
        if self.x < 0:
            return False
        elif self.x < 10:
            return True
        else:
            orn_n = self.x
            rev = 0
            while self.x != 0:
                val = self.x % 10
                rev = rev * 10 + val
                self.x //= 10
            if rev == orn_n:
                return True
            else:
                return False

print("The Pallindrome Goes\nCopyleft :- Ramrup Satpati (GPL-3)\nCredits :- Leetcode\nSollution is released as an idea and is not for cheating purposes")
attmpt = 0

while True:
    attmpt += 1
    try:
        num = int(input("Enter the Number you wish to test here : "))

        if not num:
            print("You Cant Leave the Feild Blank Like That..\n")
            ti.sleep(1)
            o.system('cls' if o.name == 'nt' else 'clear')
            s.exit()
    except (KeyboardInterrupt , EOFError) as kb:
        print("\nExitting--- Please dont spam..")
        ti.sleep(1)
        o.system('cls' if o.name == 'nt' else 'clear')
        s.exit()
    except ValueError as v:
        print("The Non Integral Values are not allowed here----\nPlease (RE)enter--")
        ti.sleep(1)
        o.system('cls' if o.name == 'nt' else 'clear')
        s.exit()
    else:
        s1 = Solution(num)
        val = s1.isPalindrome()
        print(f"Status :->\nIt is {val} that {num} is Pallindrome\n")

        print("Wanna Check a New Number (Y/N)")
        
        try:
            ch = input("Enter Your Choice (y/n) :").strip().lower()

            if ch == 'n':
                print(f"Thankyou for COming and testing the Software\nApp Used for {attmpt} time(s)\nPlease do come back")
                break   
            elif ch == 'y':
                print(f"Good! now lets Test Something else\n")
                continue
            else:
                print(f"Wrong Input---Redirecting to a y\n")
                ti.sleep(1)
                print("Redirection Successful\n")
                continue
        except (KeyboardInterrupt , EOFError) as kb:
            print("See comrade -- If you need to exit follow the rules and press n\nExit Blocked via the Keyboard Interrupt pathway\n")
            continue
        except Exception as e:
            print(f"Some Error Occurred which is caught successfully\n{e}")
            continue
    finally:
        print("Pallindrome Goes ...")