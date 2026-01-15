def check_unique(lst):
    # Your code goes here
    se_kies = list(set(lst))
    if len(se_kies) == len(lst):
        return True
    else:
        return False

