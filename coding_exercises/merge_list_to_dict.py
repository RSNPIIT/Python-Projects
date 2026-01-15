def merge_lists_to_dictionary(keys, values):
    # Your code goes here
    dit = {}
    if len(keys) != len(values):
        return False
    else:
        for i in range(len(keys)):
            dit[keys[i]] = values[i]
        return dit
