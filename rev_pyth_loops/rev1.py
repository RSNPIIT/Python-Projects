num = []
size = abs(int(input("Enter the list size here : ")))
pos_num = 0
neg_num = 0
z_num = 0
for i in range(size):
    val = float(input(f"Enter the {i+1} element in the list here : "))
    num.append(val)
    if num[i] > 0:
        pos_num += 1
    elif num[i] == 0:
        z_num += 1
    else:
        neg_num += 1
    
print(f"There are {pos_num} of positive elements in the list")
print(f"There are {neg_num} of negative elements in the list")
print(f"There are {z_num} of elements with value zero  in the list")