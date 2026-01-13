try:
    u_c = abs(int(input("Enter the Number Here :")))
except ValueError as v:
    print("Given Value aint Integer")
    exit()
else:
    val = []
    for i in range(1,8):
        val.append(i)
    if u_c in val:
        match u_c:
            case 1:
                print("\nMonday\n")
            case 2:
                print("\nTuesday\n")
            case 3:
                print("\nWednesday\n")
            case 4:
                print("\nThursday\n")
            case 5:
                print("\nFriday\n")
            case 6:
                print("\nSaturday\n")
            case 7:
                print("\nSunday\n")
    else:
        print("\nError Range in the Area\n")