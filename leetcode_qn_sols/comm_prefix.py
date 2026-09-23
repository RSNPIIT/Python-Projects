class Solution:
    def longestCommonPrefix(self, strs: List[str]) -> str:
        if not strs:
            return ''

        min_len = min(len(s) for s in strs)
        com_pref = ''
        for i in range(min_len):
            curr_ch = strs[0][i]
            if all(s[i] == curr_ch for s in strs):
                com_pref += curr_ch
            else:
                break
        return com_pref
