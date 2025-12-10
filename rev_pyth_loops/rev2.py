num = []
size = abs(int(input("Enter the list size here : ")))
pos_numsum = 0
neg_numsum = 0
z_num = 0
for i in range(size):
    val = float(input(f"Enter the {i+1} element in the list here : "))
    num.append(val)
    if num[i] > 0:
        pos_numsum += num[i]
    elif num[i] == 0:
        z_num += 0
    else:
        neg_numsum += num[i]
    
print(f"{pos_numsum} is the sum of positive elements in the list")
print(f"{neg_numsum} is the sum of negative elements in the list")
print("0 is the sum  of elements with value zero  in the list")