class Solution:
    def isMatch(self, s: str, p: str) -> bool:
        matrix = [[None] * (len(p) + 1) for _ in range(len(s) + 1)]

        def dp( i , j):
            if matrix[i][j] is not None:
                return matrix[i][j]
            
            if j == len(p):
                return i == len(s)
            
            if i == len(s):
                while j + 1 < len(p) and p[j + 1] == '*':
                    j += 2
                return j == len(p)
            
            match = s[i] == p[j] or p[j] == '.'
            if j < len(p) - 1 and p[j + 1] == '*':
                result = dp(i , j+2) or (match and dp(i + 1 , j))
            else:
                result = match and dp(i + 1, j+ 1)

            matrix[i][j] = result
            return result
        return dp(0 , 0)
