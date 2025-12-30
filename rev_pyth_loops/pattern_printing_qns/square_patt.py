n_r = abs(int(input("Enter the Number of Rows :- ")))
n_el = abs(int(input("Enter the Number of Elements in each rows :- ")))

for i in range(1, n_r + 1):
    for j in range(1 , n_el + 1):
        print(j , end = ' ')
    print('\n')