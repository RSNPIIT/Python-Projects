# Friend Recommender System

# Static Data for our sample
network = {
    "Alice": ["Bob", "Charlie", "David"],
    "Bob": ["Alice", "David", "Eve"],
    "Charlie": ["Alice", "Eve"],
    "David": ["Alice", "Bob", "Fiona"],
    "Eve": ["Bob", "Charlie"],
    "Fiona": ["David"],
    "George": ["Alice"]
}

# Looping through the keys of the Data
for person , _ in network.items():
    friends = network[person]
    fof_list = []

    for friend in friends:
        for fof in network[friend]:
            if fof != person and fof not in friends:
                fof_list.append(fof)

    counts = {}
    for sugg in set(fof_list):
        counts[sugg] = fof_list.count(sugg)
    
    ranked_fr = dict(sorted(counts.items() , key = lambda x: x[1] , reverse = True))
    people = list(ranked_fr.keys())

    if people:
        print(f"Suggestion for {person} : {people}");
    else:
        print(f"Suggestion for {person} : Not Found Any")