def is_palindromic_tuple(tup):
    # Your code goes here
    lst = list(tup)
    r_lis = list(reversed(lst))
    for i in range(len(lst)):
        if lst[i] != r_lis[i]:
            return False
        
    return True

