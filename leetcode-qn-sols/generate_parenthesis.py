class Solution:
    def generateParenthesis(self, n: int) -> List[str]:
        result = []
        def build(current , ope, close):
            if len(current) == 2*n:
                result.append(current)
                return
            if ope < n:
                build(current + '(' , ope + 1 , close)
            if close < ope:
                build(current + ')' , ope , close + 1)           
        
        build("" , 0 , 0)
        return result
