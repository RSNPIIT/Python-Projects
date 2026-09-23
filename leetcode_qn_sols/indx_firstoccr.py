class Solution:
    def strStr(self, haystack: str, needle: str) -> int:
        if needle is None:
            return 0
        if haystack is None:
            return 0
        len_hay = len(haystack)
        len_ndl = len(needle)
        for i in range(len_hay - len_ndl + 1):
            if haystack[i : i + len_ndl]== needle:
                return i
        
        return -1
