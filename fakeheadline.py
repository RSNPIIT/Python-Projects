#A Random fake funny message generator
import random
#Test Cases
subjects = [ 
    "Shahrukh Khan",
    "Virat Kohli",
    "Nirmala Sitharaman",
    "A group of monkeys",
    "Auto rickshaw driver from Delhi"
    "Prime Minister Modi"
]
actions = [
   "launches",
   "jumps",
   "eats",
   "dances",
   "has fun",
   "declares war on",
   "orders",
   "celebrates",
   "rides"
]
places =[
   "at Red Fort",
   "in Mumbai Local train",
   "a plate of Samosas",
   "inside Parliament",
   "during IPL Match",
   "at India Gate"
]
#Loop Usage
while True:
    subject = random.choice(subjects)
    action = random.choice(actions)
    place = random.choice(places)
    headline = f"BREAKING NEWS ALERT : {subject} {action} {place}"
    print("\n" + headline)
    userinp = input("\nDo yo wanna continue : (Yes/No)").strip().lower()
    if userinp == "no":
        break
#epilogue
print("\nThanks for using the Fake Headline Generator Prompt")
print("Goodbye!")
