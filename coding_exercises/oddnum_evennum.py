def count_even_odd(lst):
    # Your code goes here
    eve_cnt = 0
    od_cnt = 0
    
    for i in lst:
        if i % 2 == 0:
            eve_cnt += 1
        else:
            od_cnt += 1
        
    return (eve_cnt , od_cnt)
