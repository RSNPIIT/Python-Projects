import json as js
import pprint as pp

FILE = 'cleaned_data.json'

def load_data(data):
    with open(data) as f:
        dat = js.load(f)
    return dat

def ppl_you_may_know(user_id ,data):
    user_fr = {}
    for usr in data['users']:
        user_fr[usr['id']] = set(usr['friends'])
    
    if user_id not in user_fr:
        return []

    dir_fr = user_fr[user_id]
    sugg = {}

    for fr in dir_fr:
        for mut in user_fr:
            if mut != user_id and mut not in dir_fr:
                sugg[mut] = sugg.get(mut ,0) + 1   

    sorted_sugg = sorted(sugg.items() , key = lambda x : x[1] , reverse = True )
    usef = [user_id for user_id , _ in sorted_sugg]
    return usef

print("The Given Data is : -")
my_data = load_data(FILE)
pp.pprint(my_data)

try:
    u_id = abs(int(input("Enter the User ID to Get the Mutual Friends :-> ")))
except ValueError as v:
    print("Wrong Dataype Given\n")
    exit()
else:
    kio = ppl_you_may_know(u_id , my_data)
    print(f"Mutual Friends of {u_id} are {kio}")