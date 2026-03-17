# Note the Questions are in the Order as given by Leetcode and the sollutions are in the 'It works format'

class Solution:
    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
        lst3 = nums1 + nums2
        lst3.sort()
        med_val = 0
        # lst3 = list(set(lst3))
        if len(lst3) % 2 != 0:
            med_val = float(lst3[len(lst3) // 2])
        else:
            one_val = float(lst3[len(lst3) // 2])
            sec_val = float(lst3[(len(lst3) // 2) - 1])
            med_val = (one_val + sec_val) / 2
        return med_val