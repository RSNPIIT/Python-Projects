# The Question is to find the largest pallindromal substring

class Solution:
    def longestPalindrome(self, s: str) -> str:
        #Sollution for Empty String
        if not s:
            return ""

        long_er = ''
        for i in range(len(s)):
            #Sollution for Odd Palindrome
            l, r = i , i
            while l >= 0 and r < len(s) and s[l] == s[r]:
                if (r - l + 1) > len(long_er):
                    long_er = s[l : r + 1]
                l -= 1
                r += 1
            #Sollution for Even Pallindrome 
            l, r = i , i + 1
            while l >= 0 and r < len(s) and s[l] == s[r]:
                if(r - l + 1) > len(long_er):
                    long_er = s[l : r + 1]
                l -= 1
                r += 1
        return long_er

ghs = input("Enter the string whose pallindrome you wanna find :-> ").strip().lower()
s1 = Solution(ghs)
print(f"The Longest Pallindromal substring in {ghs.title()} is {s1.longestPalindrome()}\n")