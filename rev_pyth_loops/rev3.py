num = int(input("Enter thr value of number here : "))
mul = abs(int(input(f"Enter the number upto which you wanna multiply {num} to :  ")))
for i in range(1,mul+1):
    print(f"{num} × {i} = {num*i}")
    if i == (mul):
        break