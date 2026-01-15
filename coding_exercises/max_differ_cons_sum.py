def max_consecutive_difference(lst):
    # Your code goes here
    if len(lst) == 0:
        return False
        
    minus_lis = []
    for i in range(len(lst) -1):
        this_el = lst[i]
        the_next_el = lst[i+1]
        the_diff_I_want = abs(this_el - the_next_el)
        minus_lis.append(the_diff_I_want)
    
    the_value_I_need = max(minus_lis)
    return the_value_I_need
        

