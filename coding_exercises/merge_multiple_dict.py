def merge_three_dictionaries(dict1, dict2, dict3):
    # Your code goes here
    dict_new_mer = {}
    for (k,v) in dict1.items():
        dict_new_mer[k] = v
    for (k,v) in dict2.items():
        dict_new_mer[k] = v
    for (k,v) in dict3.items():
        dict_new_mer[k] = v
    return dict_new_mer
