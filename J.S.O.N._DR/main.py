import json as js

FILE = 'data.json'
NFILE = 'data2.json'
#Reading the JSON Data
def read_json_val(file):
    with open(file) as f:
        val = js.load(f)
    return val

# jkl = read_json_val(FILE)
# print(read_json_val(FILE))

def gimme_name(urs):
    print("\nUsers and Their Connections\n")
    for u in urs['users']:
        like_pg = []
        for pi in u['liked_pages']:
            for j in urs['pages']:
                if j['id'] == pi:
                    like_pg.append(j['name'])
                    break
                
        print(f"{u['name']} is Friends with ID {u['friends']} and Liked Pages are {like_pg}\n")
    
    print("\nPages Information\n")
    for pg in urs['pages']:
        print(f"Where the ID :{pg['id']} means {pg['name']}\n")

def clean_data(data):
    #Remove users with Missing Names
    data['users'] = [user for user in data['users'] if user['name'].strip()]
    
    #Removing the Duplicate Pages
    for u in data['users']:
        u['friends'] = list(set(u['friends']))
    
    #Now Removing the Duplicate ID Value in the Cell
    data['users'] = [user for user in data['users'] if user['friends'] or user['liked_pages']]
    
    #Now Removing the Duplicate Pages ID
    uniq_pg = {}
    for page in data['pages']:
        uniq_pg[page['id']] = page
    data['pages'] = list(uniq_pg.values())
    return data


gimme_name(read_json_val(NFILE))

with open('data2.json' , 'w') as hj:
    js.dump(clean_data(read_json_val(FILE)) , hj , indent = 4)