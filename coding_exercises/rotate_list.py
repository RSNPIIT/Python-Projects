def rotate_list(lst, k):
    # Your code goes here
    ny_l = []
    for i in range(len(lst)):
        stk = i - k
        stk %= len(lst)
        ny_l.append(lst[stk])
    return ny_l
