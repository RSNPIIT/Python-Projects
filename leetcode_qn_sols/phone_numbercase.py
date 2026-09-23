MAP = {
    '2' : 'abc',
    '3' : 'def',
    '4' : 'ghi',
    '5' : 'jkl',
    '6' : 'mno',
    '7' : 'pqrs',
    '8' : 'tuv',
    '9' : 'wxyz'
}

def backtrack(combination , next_digits , mp , result):
    if len(next_digits) == 0:
        result.append(combination)
    else:
        for letter in mp[next_digits[0]]:
            backtrack(combination + letter , next_digits[ 1 : ] , mp , result)

class Solution:
    def letterCombinations(self, digits: str) -> List[str]:
        if not digits:
            return []
        
        result = []
        backtrack( '' , digits , MAP , result)
        return result
