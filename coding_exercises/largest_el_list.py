def find_largest(numbers):
    # Your code goes here
    max_val = numbers[0]
    for i in numbers:
        if i > max_val:
            max_val = i
        else:
            max_val += 0
    return max_val
