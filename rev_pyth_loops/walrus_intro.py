#Using Walrus Operator to Append Values inside of a List (Python 3.8 and later)

inputs = []
while (current := input("Write something ('quit' to stop): ")) != "quit":
    inputs.append(current)