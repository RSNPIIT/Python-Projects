import time, os
print(r"""
                         ___________
                         \         /
                          )_______(
                          |"|_.-._,.---------.,_.-._
                          |       | | |               | | ''-.
                          |       |_| |_             _| |_..-'
                          |_______| '-' `'---------'` '-'
                          )"(
                         /_________                         `'-------'`
                       .-------------.
                      /_______________
""")

val = {}

def highest_bidder(dict):
  highest_bid = 0
  for bidder in dict:
    bid_amt = dict[bidder]
    if bid_amt > highest_bid:
      highest_bid = bid_amt
      winner = bidder
  print(f"The Winner is : {winner} with a bid of : ₹{highest_bid}")

while True:
  name = input("Enter Your name here : ").strip().title()
  price = abs(float(input("Enter Your Price Here (In INR (₹)) : ")))
  val[name] = price
  print("Are there more bidders ? (Y/N)")
  ch = input("Enter Your Choice Here (Y/N) : ").strip().lower()
  if ch == 'y':
    time.sleep(2)
    os.system('cls' if os.name == 'nt' else 'clear')
    continue
  elif ch == 'n':
    print(f"So far {len(val)} number of Bidders have registered ")
    highest_bidder(val)
    break
  else:
    print("Wrong Choice : You Gotta Enter a Y or a N no other character allowed")
    continue

