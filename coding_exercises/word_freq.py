def count_word_frequency(sentence):
    # Your code goes here
    new_thang = {}
    
    word_list = sentence.strip().split()
    for j in (word_list):
        if j in new_thang:
            new_thang[j] += 1
        else:
            new_thang[j] = 1
            
    return new_thang
