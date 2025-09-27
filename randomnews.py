import random
gen = 0
subjects = [
    "Shahrukh Khan",
    "Nirmala Sitharaman",
    "Virat Kohli",
    "Narendra Modiji the PM",
    "A Mumbai Cat",
    "A Group of Monkeys",
    "Autowala from New Delhi",
    "President D. Murmu"
    ]
actions = [
    "launches",
    "cancels",
    "dances with",
    "orders",
    "eats",
    "orders",
    "celebrates",
    "visits"
]
places_or_things = [
    "at Red Fort",
    "in Mumbai Local Train",
    "a Plate of Samosa",
    "inside parliament",
    "at Victoria Terminal",
    "at a local college",
    "during IPL Match",
    "at India Gate , New Delhi(NCR)"
]
print("-- Welcome to my Random News Generator App -- \n[Strict Warning : DON'T REPLICATE ANY GENERATED LINES AS THIS MAY MISLEAD PEOPLE AND LEAD TO LEGAL CONSEQUENCES]")
print("Made By Ramrup Satpati (RSNPIIT)")
while True:
    new = random.choice(subjects)
    action = random.choice(actions)
    place = random.choice(places_or_things)
    news_gener = new + " " + action + " " + place
    gen += 1
    print(f"{news_gener}\n")
    print("Do you Wish to Continue (any key/N) : ")
    ch = input("Enter any key to continue or a N to quit : ").strip().lower()
    if ch == 'n' or ch == 'no' :
        print(f"So far {gen} number of such funny news have been generated\n")
        break
    else:
        continue