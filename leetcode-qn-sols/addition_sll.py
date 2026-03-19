# The Question is to find the Add two numbers in a Single Linked Lists (SLL)

class Solution:
    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode(0)      
        current = dummy
        carry = 0

        while l1 or l2 or carry:
            # Get the Values and give a 0 if the list is exhausted
            val1 = l1.val if l1 else 0
            val2 = l2.val if l2 else 0

            # Compute sum and carry
            total = val1 + val2 + carry
            carry = total // 10
            digit = total % 10

            # Append result digit
            current.next = ListNode(digit)
            current = current.next

            # Advance pointers
            if l1: l1 = l1.next
            if l2: l2 = l2.next

        return dummy.next

l1 = ListNode(9)
l1.next = ListNode(9)

l2 = ListNode(1)

sol = Solution()
result = sol.addTwoNumbers(l1, l2)

while result:
    print(result.val, end=" -> " if result.next else "")
    result = result.next
