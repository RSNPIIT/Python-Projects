import json as js
import pprint as pp

FILENAME = 'cleaned_data.json'

def get_data(data):
    with open(data) as f:
        dat = js.load(f)
    return dat

def pgs_may_like(user_id , data):
    lik_pg = {}
    for usr in data['users']:
        lik_pg[usr['id']] = set(usr['liked_pages'])
    
    if user_id not in lik_pg:
        return []
    
    user_liked_pages = lik_pg[user_id]
    page_sugg = {}

    for other_user , pages in lik_pg.items():
        if other_user != user_id:
            shared_pgs = user_liked_pages.intersection(pages)

        for page in pages:
            if page not in user_liked_pages:
                page_sugg[page] = page_sugg.get(page , 0) + len(shared_pgs)
            
    sorted_pgs = sorted(page_sugg.items() , key = lambda x : x[1] , reverse = True)
    return [page_id for page_id ,_ in sorted_pgs]

my_data = get_data(FILENAME)
print("The Given Data is :- \n")
pp.pprint(my_data)

try:
    u_id = abs(int(input("Enter the User ID Here :- ")))
except ValueError as v:
    print("Wrong Data Type Given")
    exit()
val = pgs_may_like(u_id ,my_data)
print(f"The Recommended Pages are :- {val}")