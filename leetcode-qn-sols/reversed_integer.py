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


x = 100132
s1 = Solution()
print(f"The Reverse of {x} is {s1.reverse(x)}")