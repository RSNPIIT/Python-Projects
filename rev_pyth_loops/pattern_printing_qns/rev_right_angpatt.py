n_r = abs(int(input("Enter the Number of Rows :- ")))

for i in range(1 , n_r + 1):
    for j in range(1 , n_r + 1):
        if j >= i:
            print(j , end = ' ')
        else:
            print(' ' , end = ' ')
    print('\n')