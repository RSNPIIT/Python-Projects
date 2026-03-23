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

try:
    num = int(input("Enter the Number you wish to test here : "))

    if not num:
        print("You Cant Leave the Feild Blank Like That..\n")
        ti.sleep(1)
        o.system('cls' if o.name == 'nt' else 'clear')
        s.exit()
except (KeyboardInterrupt , EOFError) as kb:
    print("Exitting--- Please dont spam..")
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
finally:
    print("The Pallindrome Goes\nCopyleft :- Ramrup Satpati (GPL-3)\nCredits :- Leetcode\nSollution is released as an idea and is not for cheating purposes")