# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next

class Solution:
    def reverseKGroup(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        arr = []
        current = head
        while current:
            arr.append(current.val)
            current = current.next

        for i in range(0 , len(arr) , k):
            if (i + k) <= len(arr):
                arr[i : i + k] = reversed(arr[i : i + k])
            
        dummy = ListNode(0)
        current = dummy

        for num in arr:
            current.next = ListNode(num)
            current = current.next

        return dummy.next
