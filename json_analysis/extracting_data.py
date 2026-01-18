import json as js
import pprint as pp

FILENAME = 'data.json'

def load_data(data):
    with open(data) as r:
        dat = js.load(r)
    return dat

def display_data(data):
    print("\nUsers and Their Information :\n")
    for usr in data['users']:
        like_pgs = []
        for u in usr['liked_pages']:
            for pi in data['pages']:
                if u == pi['id']:
                    like_pgs.append(pi['name'])
                    break
                else:
                    continue

        print(f"The User Name {usr['name']} is Friends with {usr['friends']} and Likes These Pages {like_pgs}")

    print("\nPages Information :\n")
    for usr in data['pages']:
        print(f"Page Id {usr['id']} is {usr['name']}")

my_data = load_data(FILENAME)
pp.pprint(my_data)
dis_dat = display_data(my_data)
print(dis_dat)