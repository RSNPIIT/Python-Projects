#Cleaning the set data
import json as js
import pprint as pp

FILENAME = 'data.json'
NFILE = 'cleaned_data.json'

def clean_data(data):
    # First Removing the People Without Names and Removing the duplicate Friends and Remo
    data['users'] = [u for u in data['users'] if u['name'].strip()]
    for j in data['users']:
        j['friends'] = list(set(j['friends']))

    data['users'] = [u for u in data['users'] if u['friends'] and u['liked_pages']]
    
    # Remove Duplicate Pages
    uniq_pgs = {}
    for pg in data['pages']:
        uniq_pgs[pg['id']] = pg
    data['pages'] = list(uniq_pgs.values())
    return data

def get_data(data):
    with open(data) as f:
        dat = js.load(f)
    return dat

def display_data(data): 
    print("\nUsers and Their Information :\n")
    for dat in data['users']:
        like_pgs = []
        for pi in dat['liked_pages']:
            for k in data['pages']:
                if pi == k['id']:
                    like_pgs.append(k['name'])
                    break
                else:
                    continue
        print(f"{dat['name']} is friends with {dat['friends']} and likes these pages -> {like_pgs}")

    print("\nPages Information :\n")
    for dat in data['pages']:
        print(f"{dat['id']} :-> {dat['name']}")

with open(NFILE , 'w') as k:
    js.dump(clean_data(get_data(FILENAME)) , k ,indent = 4)

my_data = get_data(NFILE)
print("The JSON is :->\n")
pp.pprint(my_data)
display_data(my_data)