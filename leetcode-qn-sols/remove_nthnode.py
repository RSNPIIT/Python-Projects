# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def removeNthFromEnd(self, head: Optional[ListNode], n: int) -> Optional[ListNode]:
        dummy = ListNode(0)
        dummy.next = head

        # We make two pointers (In Python you dont have * and & (Even I dont know why did mr Dennis added these))
        rabbit = dummy
        turtle = dummy

        # Now we move the Pointer rabbit to till the nth position 
        # Basically give rabbit a headstart
        for _ in range(n + 1):
            rabbit = rabbit.next

        # This unless the Rabbit falls of the turtle proceeds
        while rabbit:
            rabbit = rabbit.next
            turtle = turtle.next
        
        # Now we simply jump off the value
        turtle.next = turtle.next.next
        
        return dummy.next
        
