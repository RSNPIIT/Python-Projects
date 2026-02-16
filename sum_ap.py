n = abs(int(input("Enter the Value upto which youre gonna sum : ")))

sum = 0
for i in range(1 , n+1):
    sum += i**2 * (n - i + 1)

print(f"The Final GP sum is : {sum}") 