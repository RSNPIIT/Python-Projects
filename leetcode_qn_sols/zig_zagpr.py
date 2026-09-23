class Solution:
    def convert(self, s: str, numRows: int) -> str:
        if numRows == 1 or len(s) <= numRows:
            return s
        else:
            res = [''] * numRows
            index = 0
            step = 1
            for ch in s:
                res[index] += ch

                if index == 0:
                    step = 1
                elif index == numRows - 1:
                    step = -1
                index += step
            return ''.join(res)
