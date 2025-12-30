n_r = abs(int(input("Enter the Number of Rows :- ")))

for i in range(1 , n_r + 1) :
    for _ in range(n_r - i):
        print(' ' , end = ' ')
    
    for j in range(i , 0 , -1):
        print(j , end = ' ')

    print('\n')