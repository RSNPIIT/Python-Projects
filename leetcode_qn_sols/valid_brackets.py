MATCH_CASE = {
    ')' : '(',
    '}' : '{',
    ']' : '[',
}

OPN_BR = '({['

class Solution:
    def isValid(self, s: str) -> bool:
        stack = []
        for char in s:
            if char in OPN_BR:
                stack.append(char)
            else:
                if not stack:
                    return False
                elif stack[-1] != MATCH_CASE[char]:
                    return False
                stack.pop()
        
        if len(stack) == 0:
            return True
        else:
            return False
