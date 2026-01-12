#Taking the Average and the Deviation here
try:
    n = int(input("Enter the Value Here : "))
    n2 = int(input("Enter the 2nd Value Here : "))

except ValueError:
    print("Wrong Value \nNot Allowed\n")
    exit()

else:
    val_at_ones = n % 10
    print(f"\nOnes Place Value is : {val_at_ones}")

    avg = 0.5*(n + n2)
    dev1 = avg - n
    print(f"\n1st Deviation is :- {dev1}")
    dev2 = avg - n2
    print(f"\n2nd Deviation is :- {dev2}")

    var = (dev1 ** 2 + dev2 ** 2) ** 0.5
    print(f"{var}")


finally:
    pass