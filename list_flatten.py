# The Code for Flattening a list 

def flatten_list_fl(lis):
    lid = []

    for its in lis:
        if isinstance(its ,list):
            lid.extend(flatten_list_fl(its))
        else:
            lid.append(its)
    return lid

lij = [56 , 64 , [62 , 74 , 123 , 441] , [[56 , 74 , 234 , 11 , [456 , 444 , 333 , 222 , 127 ], 0 , 46 , 23] , 19 , 21 , 24] , 320]
x = flatten_list_fl(lij)
print(f"The Original List is :- \n{lij}\nAnd the Flattened list is {x}")

print("\nMade by 🄯RSNPIIT (Ramrup Satpati) an Open Source Enthusiast and Evangelist from IIT Madras\nThis Code is Released under the GNU GPLv3 License\nMade using Codium and Python and Git")