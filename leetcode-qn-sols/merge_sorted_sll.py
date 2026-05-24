# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next

class Solution:
    def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:
        arr = []
        for list in lists:
            while list:
                arr.append(list.val)
                list = list.next
        
        arr.sort()
        dummy = ListNode(0)
        current = dummy
        for num in arr:
            current.next = ListNode(num)
            current = current.next
        
        return dummy.next
